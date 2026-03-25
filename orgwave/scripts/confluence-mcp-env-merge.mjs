/**
 * Shared Confluence MCP credential merge (same order as Cursor + launcher):
 * fill empty CONFLUENCE_* from ~/.cursor/confluence-mcp.env, ~/.config/orgwave/, ~/.zshrc.
 * Cursor applies mcp.json `env` + `envFile` before the launcher runs; CLI probes must load `.env` first.
 */
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

export const CONFLUENCE_ENV_KEYS = [
  "CONFLUENCE_USER_EMAIL",
  "CONFLUENCE_API_TOKEN",
  "CONFLUENCE_BASE_URL",
];

/** Matches `mcp-servers/servers/confluence.json` — used when BASE_URL still empty. */
export const CONFLUENCE_PINNED_BASE_URL =
  "https://confluence.myntracorp.com/";

function shSingleQuote(s) {
  return `'${s.replace(/'/g, `'\"'\"'`)}'`;
}

export function loadRepoDotEnvConfluenceKeys(repoRoot) {
  const envPath = path.join(repoRoot, ".env");
  let text;
  try {
    text = fs.readFileSync(envPath, "utf8");
  } catch {
    return;
  }
  const keyRe = new RegExp(
    `^(?:export\\s+)?(${CONFLUENCE_ENV_KEYS.join("|")})\\s*=\\s*(.*)$`
  );
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
    process.env[m[1]] = val;
  }
}

export function mergeConfluenceEnvFromUserLayers() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (home) {
    const candidates = [
      path.join(home, ".cursor", "confluence-mcp.env"),
      path.join(home, ".config", "orgwave", "confluence-mcp.env"),
    ];
    const keyRe = new RegExp(
      `^(?:export\\s+)?(${CONFLUENCE_ENV_KEYS.join("|")})\\s*=\\s*(.*)$`
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

  if (process.platform === "win32") return;
  const homeOnly = process.env.HOME;
  if (!homeOnly) return;
  const zshrc = path.join(homeOnly, ".zshrc");
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
  const keysLiteral = JSON.stringify(CONFLUENCE_ENV_KEYS);
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
      env: { ...process.env, HOME: homeOnly },
      stdio: ["ignore", "pipe", "pipe"],
    }).trim();
    if (!out) return;
    const parsed = JSON.parse(out);
    for (const k of CONFLUENCE_ENV_KEYS) {
      const v = parsed[k];
      if (v && String(v).trim() && !process.env[k]?.trim()) {
        process.env[k] = String(v).trim();
      }
    }
  } catch {
    /* .zshrc may write to stdout or be incompatible with non-interactive source */
  }
}
