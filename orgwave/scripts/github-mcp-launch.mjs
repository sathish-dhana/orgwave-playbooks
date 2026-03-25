#!/usr/bin/env node
/**
 * Launch @modelcontextprotocol/server-github with a PAT (same resolution as the old shell wrapper).
 * - Local runtime: dynamic import so MCP uses this process stdin/stdout directly (no wrapper child).
 * - `gh auth token` uses execFileSync with stdin ignored so JSON-RPC on fd 0 is never consumed.
 */
import { spawn, execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");
const runtimeEntry = path.join(
  repoRoot,
  "orgwave/mcp-runtime/node_modules/@modelcontextprotocol/server-github/dist/index.js"
);

const GITHUB_TOKEN_KEYS = [
  "GITHUB_PERSONAL_ACCESS_TOKEN",
  "GITHUB_TOKEN",
  "GH_TOKEN",
];

function hasAnyGithubPatHint() {
  return GITHUB_TOKEN_KEYS.some((k) => process.env[k]?.trim());
}

/** POSIX single-quoted shell word for an arbitrary string. */
function shSingleQuote(s) {
  return `'${s.replace(/'/g, `'\"'\"'`)}'`;
}

/**
 * Cursor started from Dock / deeplinks often inherits no shell profile. If the user exports
 * GITHUB_TOKEN only in ~/.zshrc, source that file (non-interactive; stderr/stdout noise ignored)
 * and copy token vars into this process before falling back to `gh auth token`.
 */
function loadGithubTokensFromZshrc() {
  if (hasAnyGithubPatHint()) return;
  if (process.platform === "win32") return;
  const home = process.env.HOME;
  if (!home) return;
  const zshrc = path.join(home, ".zshrc");
  try {
    if (!fs.statSync(zshrc).isFile()) return;
  } catch {
    return;
  }
  const zshBin = fs.existsSync("/bin/zsh")
    ? "/bin/zsh"
    : fs.existsSync("/usr/bin/zsh")
      ? "/usr/bin/zsh"
      : null;
  if (!zshBin) return;
  const nodeProbe = String.raw`const k=["GITHUB_PERSONAL_ACCESS_TOKEN","GITHUB_TOKEN","GH_TOKEN"];const o={};for(const x of k){const v=process.env[x];if(v&&String(v).trim())o[x]=String(v).trim();}process.stdout.write(JSON.stringify(o));`;
  const probe = [
    "set +e;",
    `[ -r ${shSingleQuote(zshrc)} ] && . ${shSingleQuote(zshrc)} 2>/dev/null;`,
    `${shSingleQuote(process.execPath)} -e ${shSingleQuote(nodeProbe)}`,
  ].join(" ");
  try {
    const out = execFileSync(zshBin, ["-c", probe], {
      encoding: "utf8",
      maxBuffer: 64 * 1024,
      env: { ...process.env, HOME: home },
      stdio: ["ignore", "pipe", "pipe"],
    }).trim();
    if (!out) return;
    const parsed = JSON.parse(out);
    for (const k of GITHUB_TOKEN_KEYS) {
      const v = parsed[k];
      if (v && String(v).trim() && !process.env[k]?.trim()) {
        process.env[k] = String(v).trim();
      }
    }
  } catch {
    /* .zshrc may write to stdout or be incompatible with non-interactive source */
  }
}

/** Cursor opened from Dock / GitHub “Run in Cursor” often has a minimal PATH — gh lives in Homebrew. */
function ensureMcpPath() {
  const extra = ["/opt/homebrew/bin", "/usr/local/bin"].filter((d) => {
    try {
      return fs.statSync(d).isDirectory();
    } catch {
      return false;
    }
  });
  const parts = (process.env.PATH || "")
    .split(path.delimiter)
    .filter(Boolean);
  const seen = new Set(parts);
  const prefix = extra.filter((d) => !seen.has(d));
  if (prefix.length) process.env.PATH = [...prefix, ...parts].join(path.delimiter);
}

/**
 * Deeplinks cannot inject secrets. When Cursor’s process has no GITHUB_TOKEN, load optional user file
 * (one-time setup) so GitHub MCP still authenticates after “Run in Cursor” from GitHub.
 */
function loadUserGithubMcpEnvFile() {
  if (hasAnyGithubPatHint()) {
    return;
  }
  const home = process.env.HOME || process.env.USERPROFILE;
  if (!home) return;
  const candidates = [
    path.join(home, ".cursor", "github-mcp.env"),
    path.join(home, ".config", "orgwave", "github-mcp.env"),
  ];
  for (const filePath of candidates) {
    let text;
    try {
      text = fs.readFileSync(filePath, "utf8");
    } catch {
      continue;
    }
    for (const raw of text.split(/\n/)) {
      const line = raw.replace(/^\uFEFF/, "").trim();
      if (!line || line.startsWith("#")) continue;
      const m = line.match(
        /^(?:export\s+)?(GITHUB_PERSONAL_ACCESS_TOKEN|GITHUB_TOKEN|GH_TOKEN)\s*=\s*(.*)$/
      );
      if (!m) continue;
      let val = m[2].trim();
      if (
        (val.startsWith('"') && val.endsWith('"')) ||
        (val.startsWith("'") && val.endsWith("'"))
      ) {
        val = val.slice(1, -1);
      }
      const key = m[1];
      if (!process.env[key]?.trim()) process.env[key] = val;
    }
    if (hasAnyGithubPatHint()) {
      break;
    }
  }
}

function resolvePat() {
  if (process.env.GITHUB_PERSONAL_ACCESS_TOKEN?.trim()) return;
  if (process.env.GITHUB_TOKEN?.trim()) {
    process.env.GITHUB_PERSONAL_ACCESS_TOKEN = process.env.GITHUB_TOKEN.trim();
    return;
  }
  if (process.env.GH_TOKEN?.trim()) {
    process.env.GITHUB_PERSONAL_ACCESS_TOKEN = process.env.GH_TOKEN.trim();
    return;
  }
  const ghBins = ["/opt/homebrew/bin/gh", "/usr/local/bin/gh", "gh"];
  const ghEnv = { ...process.env, GIT_TERMINAL_PROMPT: "0" };
  for (const gh of ghBins) {
    try {
      const t = execFileSync(gh, ["auth", "token"], {
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"],
        env: ghEnv,
      }).trim();
      if (t) {
        process.env.GITHUB_PERSONAL_ACCESS_TOKEN = t;
        return;
      }
    } catch {
      /* try next */
    }
  }
}

function forwardExit(child) {
  child.on("error", (err) => {
    console.error(err);
    process.exit(1);
  });
  child.on("exit", (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    else process.exit(code === null ? 1 : code);
  });
}

ensureMcpPath();
loadUserGithubMcpEnvFile();
loadGithubTokensFromZshrc();
resolvePat();

if (fs.existsSync(runtimeEntry)) {
  await import(pathToFileURL(runtimeEntry).href);
} else {
  const isWin = process.platform === "win32";
  const npx = isWin ? "npx.cmd" : "npx";
  forwardExit(
    spawn(
      npx,
      ["-y", "--package=@modelcontextprotocol/server-github", "--", "mcp-server-github"],
      {
        stdio: "inherit",
        env: { ...process.env },
        shell: isWin,
        windowsHide: true,
      }
    )
  );
}
