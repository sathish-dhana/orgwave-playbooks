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
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

import { mergeConfluenceEnvFromUserLayers } from "./confluence-mcp-env-merge.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");
const runtimeEntry = path.join(
  repoRoot,
  "orgwave/mcp-confluence-runtime/node_modules/@answerai/confluence-mcp/build/index.js"
);

mergeConfluenceEnvFromUserLayers();

if (!fs.existsSync(runtimeEntry)) {
  console.error(
    "[confluence-mcp-launch] Missing pinned runtime. Run: cd orgwave/mcp-confluence-runtime && npm ci"
  );
  process.exit(1);
}

await import(pathToFileURL(runtimeEntry).href);
