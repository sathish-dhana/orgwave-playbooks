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
| **Secrets** | **GitHub:** `export GITHUB_TOKEN=…` in **`~/.zshrc`**, then **`source ~/.zshrc`** and **start Cursor from that terminal** so MCP sees it; or optional repo **`.env`** with **`GITHUB_PERSONAL_ACCESS_TOKEN`** (see **`.env.example`**). Deeplinks cannot inject tokens. |
| **Reload** | After changing **`mcp.json`**, reload Cursor or restart if tools do not appear. |
| **Tool approval** | Cursor may prompt per tool; the agent should **fall back to `gh`** rather than block if MCP stalls. |
| **Enable server** | If a server is **listed but disabled**, turn it **on** in Cursor (see **Enabling a disabled MCP server** below) so tools reach the agent. |

### If you already set tokens — is it “auto”?

When **`GITHUB_TOKEN`** is in the environment **of the Cursor process** (e.g. exported in **`~/.zshrc`** and Cursor launched **from a terminal** after `source ~/.zshrc`), GitHub MCP can start without extra steps. The macOS **Dock** icon often does **not** load `~/.zshrc` — use **`open -a Cursor …`** from that shell, or repo **`.env`** with **`GITHUB_PERSONAL_ACCESS_TOKEN`**.

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

## Enabling a disabled MCP server

**Symptom:** The server **appears** under **Cursor Settings → Tools & MCP** (names may vary slightly by Cursor version), but it is **off**, **disabled**, or **not running** — so the agent gets **no tools** from that server even though **`mcp-servers/servers/<id>.json`** and **`.cursor/mcp.json`** are correct.

**Do this:**

1. Open **Cursor Settings** → **Tools & MCP** (or the MCP section in **Features**).
2. Find the server by its **id** — the same key as in **`.cursor/mcp.json`** under **`mcpServers`** (e.g. **`github`** for GitHub). Project servers from **orgwave-playbooks** only load when the workspace folder is this repo root (see *GitHub MCP missing in Cursor*).
3. **Enable** / turn **on** the server. If Cursor shows an error, fix **env vars** (see **`mcp-servers/README.md`** and the **`_orgwave.env`** list in that server’s JSON) and try again.
4. **Command Palette → Developer: Reload Window** if tools still do not show for the agent.

**For agents:** Prefer MCP once tools are available; if the user says the server was disabled, point them here and continue with **`gh`** / REST / **`discovery-output.json`** until they enable it — do not block the playbook on UI toggles.

## GitHub MCP missing in Cursor

**Symptom:** **Tools & MCP** lists other servers (e.g. Grafana, New Relic) but **no `github`** entry, or the agent never sees GitHub MCP tools.

**Cause:** Cursor reads **project** MCP from **`.cursor/mcp.json` in the workspace root**. Running OrgWave with the workspace opened on a **parent folder** (multi-project tree, monorepo root, or `IdeaProjects`) does **not** load **orgwave-playbooks**’s `.cursor/mcp.json`, so **GitHub MCP is never started**. Playbooks also **cannot** create that connection at runtime—it is configuration, not something the agent registers by following `SKILL.md`.

**Fix:**

1. **File → Open Folder** and choose the **`orgwave-playbooks`** directory itself (the folder that contains **`orgwave/catalog.yaml`** and **`.cursor/mcp.json`**).
2. **Command Palette → Developer: Reload Window** (or restart Cursor).
3. Confirm **`.cursor/mcp.json`** contains **`mcpServers.github`**; if not, from repo root run **`python3 orgwave/scripts/build-mcp-json.py`** and reload again.
4. Ensure **`GITHUB_TOKEN`** reaches the Cursor process (see **`mcp-servers/README.md`**) or use repo **`.env`** with **`GITHUB_PERSONAL_ACCESS_TOKEN`** per **`.env.example`**.

After that, **github** should appear alongside any **user-level** MCP servers. If **github** is listed but **disabled**, use **Enabling a disabled MCP server** above. Until the server is available, OrgWave correctly falls back to **`gh`** or the GitHub REST API.
