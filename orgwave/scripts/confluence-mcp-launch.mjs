#!/usr/bin/env node
/**
 * Launch @answerai/confluence-mcp with credentials merged like GitHub MCP:
 * - Cursor already applied mcp.json `env` + workspace `envFile` (.env).
 * - Then ~/.cursor/confluence-mcp.env (and ~/.config/orgwave/) fill only empty keys.
 * - Then ~/.zshrc is sourced non-interactively; CONFLUENCE_* are copied for keys still empty
 *   (Dock / deep-link launches often have no shell profile in the parent).
 *
 * Does not write .env (avoids races with MCP startup and accidental commits).
 */
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");
const runtimeEntry = path.join(
  repoRoot,
  "orgwave/mcp-confluence-runtime/node_modules/@answerai/confluence-mcp/build/index.js"
);

const CONFLUENCE_KEYS = [
  "CONFLUENCE_USER_EMAIL",
  "CONFLUENCE_API_TOKEN",
  "CONFLUENCE_BASE_URL",
];

/** POSIX single-quoted shell word for an arbitrary string. */
function shSingleQuote(s) {
  return `'${s.replace(/'/g, `'\"'\"'`)}'`;
}

/**
 * Merge user-level env files into process.env for keys that are still empty.
 */
function loadUserConfluenceMcpEnvFile() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (!home) return;
  const candidates = [
    path.join(home, ".cursor", "confluence-mcp.env"),
    path.join(home, ".config", "orgwave", "confluence-mcp.env"),
  ];
  const keyRe = new RegExp(
    `^(?:export\\s+)?(${CONFLUENCE_KEYS.join("|")})\\s*=\\s*(.*)$`
  );
  for (const filePath of candidates) {
    let text;
    try {
      text = fs.readFileSync(filePath, "utf8");
    } catch {
      continue;
    }
    for (const raw of text.split("\n")) {
      const line = raw.replace(/^\uFEFF/, "").trim();
      if (!line || line.startsWith("#")) continue;
      const m = line.match(keyRe);
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
  }
}

/**
 * Source ~/.zshrc non-interactively and copy CONFLUENCE_* into this process only when empty.
 */
function loadConfluenceFromZshrc() {
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
  const keysLiteral = JSON.stringify(CONFLUENCE_KEYS);
  const nodeProbe = `const k=${keysLiteral};const o={};for(const x of k){const v=process.env[x];if(v&&String(v).trim())o[x]=String(v).trim();}process.stdout.write(JSON.stringify(o));`;
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
    for (const k of CONFLUENCE_KEYS) {
      const v = parsed[k];
      if (v && String(v).trim() && !process.env[k]?.trim()) {
        process.env[k] = String(v).trim();
      }
    }
  } catch {
    /* .zshrc may write to stdout or be incompatible with non-interactive source */
  }
}

loadUserConfluenceMcpEnvFile();
loadConfluenceFromZshrc();

if (!fs.existsSync(runtimeEntry)) {
  console.error(
    "[confluence-mcp-launch] Missing pinned runtime. Run: cd orgwave/mcp-confluence-runtime && npm ci"
  );
  process.exit(1);
}

await import(pathToFileURL(runtimeEntry).href);
