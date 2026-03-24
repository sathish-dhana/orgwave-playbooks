# MCP servers for OrgWave

This file is the **policy** for how the agent uses MCP. **Machine definitions** live in the top-level **`mcp-servers/`** folder (see below).

## Policy: do not block the user on MCP

OrgWave is designed so **discovery and playbooks keep going** even if MCP is down or misconfigured:

- **`mcp-servers/servers/*.json`** describe each server; **`python3 orgwave/scripts/build-mcp-json.py`** merges them into **`.cursor/mcp.json`**, which Cursor loads. When env tokens are visible to Cursor, those servers **can** auto-start.
- If MCP is unavailable, errors, or the user has not approved tool calls, the agent must **`gh`** and/or **`discovery-output.json`** **without stopping** to fix MCP first.
- The only intentional **stop** in the flow is **after** listing candidates, until the user **selects which repos** to change (or merge) — not for MCP setup.

## Where things live

| Path | Role |
|------|------|
| **`mcp-servers/README.md`** | **How to add a server** — filename, JSON shape, `_orgwave` metadata, `${env:…}` secrets. |
| **`mcp-servers/servers/<id>.json`** | **Source of truth** per MCP server (one file per `<id>`). |
| **`orgwave/scripts/build-mcp-json.py`** | Merges `servers/*.json` → **`.cursor/mcp.json`**. Run after adding/editing server files. |
| **`.cursor/mcp.json`** | **Generated** — Cursor’s project MCP file ([docs](https://cursor.com/docs/context/mcp)). Commit it after running the script. |
| **`orgwave/required-mcp.md`** (this file) | **Behaviour** — non-blocking, fallbacks, auto-run notes. |

## What can be automated?

**Partly yes:** `.cursor/mcp.json` tells Cursor **which commands/URLs** to run for each server. **`${env:VAR}`** pulls tokens from the environment — no secrets in git.

| Step | Why |
|------|-----|
| **Secrets** | Set env vars named in each server’s **`_orgwave.env`** (see `mcp-servers/servers/*.json`). |
| **Reload** | After changing **`mcp.json`**, reload Cursor or restart if tools do not appear. |
| **Tool approval** | Cursor may prompt per tool; the agent should **fall back to `gh`** rather than block if MCP stalls. |

### If you already set tokens — is it “auto”?

When **`GITHUB_TOKEN`** (and any other declared vars) are visible to Cursor’s MCP process, matching servers should connect **without** a separate manual “connect” step — subject to Cursor and OS env inheritance (see earlier notes in git history / macOS Dock).

### Can Auto-run be set from a prompt / this repo?

**No.** Use Cursor **Agent** auto-run settings and optional **`~/.cursor/permissions.json`** — see **`mcp-servers/README.md`** (`permissionsAllowlistHint` per server) and [permissions.json reference](https://cursor.com/docs/reference/permissions). Patterns use the same **`<id>`** as `mcp-servers/servers/<id>.json` (e.g. `github:*`).

## Required (default)

| Server | Definition | Purpose |
|--------|------------|---------|
| **GitHub** | `mcp-servers/servers/github.json` | Repo list/filter for discovery (same class of data as `gh` when MCP is down). |

## Optional

Add **`mcp-servers/servers/<new-id>.json`**, run **`build-mcp-json.py`**, document in playbook **`SKILL.md`** if a playbook **requires** that integration for non-discovery steps.

## Rules for playbooks

- Do **not** embed MCP server commands in playbooks; add **`mcp-servers/servers/<id>.json`** and merge.
- The orchestrator always allows **`gh`** / **`discovery-output.json`** as discovery fallbacks.

## Changing MCP servers

1. Add or edit **`mcp-servers/servers/<id>.json`** (see **`mcp-servers/README.md`**).
2. Run **`python3 orgwave/scripts/build-mcp-json.py`** and commit **`.cursor/mcp.json`**.
3. Update **`orgwave/required-mcp.md`** tables if the default set changes.
4. If deeplink wording must change, edit **`build_prompt()`** in `orgwave/scripts/generate-orgwave-deeplink.py` and run **`python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`**.
