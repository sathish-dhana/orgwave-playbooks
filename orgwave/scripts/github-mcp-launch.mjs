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
