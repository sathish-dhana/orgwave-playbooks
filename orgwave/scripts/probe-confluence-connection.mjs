#!/usr/bin/env node
/**
 * Verifies Confluence REST auth the same way as @answerai/confluence-mcp (Basic email:token).
 *
 * Cursor showing "connected" only means the MCP stdio process started — it does not prove
 * the Confluence API accepts your credentials.
 *
 * Usage (from repo root):
 *   node orgwave/scripts/probe-confluence-connection.mjs
 *   node orgwave/scripts/probe-confluence-connection.mjs --verbose
 *
 * Resolves env like the MCP child: repo `.env`, pinned BASE_URL if still empty, then
 * ~/.cursor/confluence-mcp.env, ~/.config/orgwave/confluence-mcp.env, ~/.zshrc (fill empty only).
 */
import process from "node:process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import {
  CONFLUENCE_ENV_KEYS,
  CONFLUENCE_PINNED_BASE_URL,
  loadRepoDotEnvConfluenceKeys,
  mergeConfluenceEnvFromUserLayers,
} from "./confluence-mcp-env-merge.mjs";

const verbose = process.argv.includes("--verbose") || process.argv.includes("-v");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");

loadRepoDotEnvConfluenceKeys(repoRoot);
if (!process.env.CONFLUENCE_BASE_URL?.trim()) {
  process.env.CONFLUENCE_BASE_URL = CONFLUENCE_PINNED_BASE_URL;
}
mergeConfluenceEnvFromUserLayers();

const email = process.env.CONFLUENCE_USER_EMAIL?.trim();
const token = process.env.CONFLUENCE_API_TOKEN?.trim();
let baseUrl = process.env.CONFLUENCE_BASE_URL?.trim() || CONFLUENCE_PINNED_BASE_URL;
if (!baseUrl.endsWith("/")) baseUrl += "/";

const missing = CONFLUENCE_ENV_KEYS.filter((k) => !process.env[k]?.trim());
if (missing.length) {
  console.error(
    "[probe-confluence] Missing or empty:",
    missing.join(", "),
    "\nSet them in repo .env, ~/.cursor/confluence-mcp.env, or ~/.zshrc (see mcp-servers/README.md)."
  );
  process.exit(1);
}

if (verbose) {
  console.error("[probe-confluence] Base URL:", baseUrl);
  console.error("[probe-confluence] Email:", email);
  console.error(
    "[probe-confluence] Token:",
    token ? `set (${token.length} chars)` : "(empty)"
  );
}

const auth = Buffer.from(`${email}:${token}`).toString("base64");
const url = new URL("rest/api/space", baseUrl);
url.searchParams.set("limit", "1");

let res;
try {
  res = await fetch(url, {
    headers: {
      Authorization: `Basic ${auth}`,
      Accept: "application/json",
    },
  });
} catch (e) {
  console.error("[probe-confluence] Network error:", e instanceof Error ? e.message : e);
  process.exit(2);
}

if (res.ok) {
  console.log(
    "Confluence API OK:",
    res.status,
    `(same Basic auth scheme as Confluence MCP — not only "connected" in Cursor)`
  );
  process.exit(0);
}

let detail = res.statusText;
try {
  const body = await res.json();
  if (body?.message) detail = body.message;
} catch {
  /* ignore */
}

console.error(
  "[probe-confluence] Confluence API failed:",
  res.status,
  detail,
  "\n401/403: wrong or expired token, wrong email, or .env overriding zshrc with empty values."
);
process.exit(2);
