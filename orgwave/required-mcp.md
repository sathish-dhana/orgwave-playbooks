# MCP servers for OrgWave

This file is **policy** for how the agent uses MCP. **Server definitions** live in **`mcp-servers/`** (see **`mcp-servers/README.md`**).

## Policy

- Playbooks list **MCP servers required** in **`playbooks/<id>/SKILL.md`**. For each required **`id`**, the agent uses **only** that server’s tools for steps the playbook assigns to it.
- **Stop** (do not substitute shell, **`gh`**, or ad-hoc REST) when any of the following is true:
  - **`mcpServers.<id>`** is **missing** from **`.cursor/mcp.json`** at the workspace root.
  - The server is **disabled** in **Cursor → Settings → Tools & MCP**, or tools for that server **do not attach** to the agent session.
  - **401** / **403** / **Requires authentication** from that server’s tools after **one** reasonable retry — treat as **PAT / enable / reload** (see checklist below).
- When prerequisites pass, **continue** with MCP only.
- The usual **stop** for repo selection (after the numbered discovery table) is separate from the MCP gate.

## Where things live

| Path | Role |
|------|------|
| **`mcp-servers/README.md`** | **How to add a server** — JSON shape, `_orgwave` metadata, `${env:…}` secrets, token merge for GitHub. |
| **`mcp-servers/servers/<id>.json`** | **Source of truth** per MCP server. |
| **`orgwave/scripts/build-mcp-json.py`** | Merges `servers/*.json` → **`.cursor/mcp.json`**. |
| **`.cursor/mcp.json`** | **Generated** — Cursor’s project MCP file ([docs](https://cursor.com/docs/context/mcp)). Commit it after running the script. |
| **`orgwave/required-mcp.md`** (this file) | **Behaviour** — MCP gate, reload, PAT pointers. |

## What can be automated?

**Partly:** `.cursor/mcp.json` tells Cursor **which commands** to run. **`${env:VAR}`** can supply secrets — none in git.

| Step | Why |
|------|-----|
| **Secrets** | **`github-mcp-launch.mjs`** builds **`GITHUB_PERSONAL_ACCESS_TOKEN`** for the GitHub MCP child: repo **`.env`** (via **`envFile`**) wins when set; then **`github-mcp.env`** / **`.zshrc`** merge into **empty** keys; then default order in **`mcp-servers/README.md`** (e.g. **`gh auth token`**, **`GITHUB_TOKEN`**). See README for **`ORGWAVE_MCP_PREFER_ENV_TOKEN`**. |
| **Pinned GitHub MCP** | Once per clone: **`cd orgwave/mcp-runtime && npm ci`** for fast startup. |
| **Reload** | After changing **`mcp.json`** or toggling servers — **Developer: Reload Window** if tools do not appear. |
| **Tool approval** | Cursor may prompt per tool; retry **once**, then **gate** if auth still fails. |
| **Enable server** | If a server is **listed but off**, turn it **on** (see below). |

### If you already set tokens — is it “auto”?

When **`.env`**, **`github-mcp.env`**, **`~/.zshrc`**, or the launcher’s default token resolution supplies a valid PAT, GitHub MCP can authenticate. The macOS **Dock** often does not load **`~/.zshrc`** into Cursor’s GUI — the launcher still **sources** **`~/.zshrc`** for the MCP child when keys are empty; you can also use **`.env`** or **`github-mcp.env`**.

### Can Auto-run be set from a prompt / this repo?

**No.** Use Cursor **Agent** settings and optional **`~/.cursor/permissions.json`** — see **`mcp-servers/README.md`** and [permissions.json reference](https://cursor.com/docs/reference/permissions).

## Required (default)

| Server | Definition | Purpose |
|--------|------------|---------|
| **GitHub** | `mcp-servers/servers/github.json` | Discovery, repo metadata, branches, files, PRs via MCP tools. |

## Optional

Add **`mcp-servers/servers/<new-id>.json`**, run **`build-mcp-json.py`**, and document the **`id`** in playbook **`SKILL.md`** if a playbook **requires** it.

| Server | Definition | Purpose |
|--------|------------|---------|
| **Confluence** | `mcp-servers/servers/confluence.json` | Confluence pages via **`@answerai/confluence-mcp`**; run **`cd orgwave/mcp-confluence-runtime && npm ci`** once. Env: **`CONFLUENCE_BASE_URL`**, **`CONFLUENCE_USER_EMAIL`**, **`CONFLUENCE_API_TOKEN`** in **`.env`**. |

## Rules for playbooks

- Do **not** embed raw MCP server launch commands in playbooks; add **`mcp-servers/servers/<id>.json`** and merge.
- Do **not** document **`gh`**, **`git`**, or REST as alternate ways to complete steps assigned to GitHub MCP.

## GitHub MCP gate — checklist for the agent when tools are missing or auth fails

1. **Workspace:** **File → Open Folder** → **`orgwave-playbooks`** repo root (folder with **`orgwave/catalog.yaml`** and **`.cursor/mcp.json`**), not a parent tree.
2. **Enable server:** **Cursor Settings → Tools & MCP** → turn **on** **`github`** (same id as **`mcpServers.github`**).
3. **PAT:** Valid token must reach the MCP process — **`mcp-servers/README.md`**: **`.env`** **`GITHUB_PERSONAL_ACCESS_TOKEN`**, **`~/.cursor/github-mcp.env`**, **`~/.zshrc`**, launcher order. Fix **401** vs **403** per the README table.
4. **Reload:** **Developer: Reload Window**, then **send a new message** so tools attach.
5. **Optional:** **`cd orgwave/mcp-runtime && npm ci`** for a fast pinned server.

## Changing MCP servers

1. Add or edit **`mcp-servers/servers/<id>.json`** (see **`mcp-servers/README.md`**).
2. Run **`python3 orgwave/scripts/build-mcp-json.py`** and commit **`.cursor/mcp.json`**.
3. Update **`orgwave/required-mcp.md`** tables if the default set changes.
4. If deeplink text must change, edit **`DEEPLINK_PROMPT_TEMPLATE`** in `orgwave/scripts/generate-orgwave-deeplink.py` and run **`python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`**.

## Making GitHub MCP available to the agent

**Agents only see MCP tools Cursor attaches to the chat.**

| Who | What to do |
|-----|------------|
| **User** | Workspace = **orgwave-playbooks** root; **Tools & MCP** → **`github`** **on**; **Reload Window** after edits to **`mcp.json`**. |
| **User** | Approve tool prompts or allowlist (e.g. **`github:*`**) per **`mcp-servers/README.md`**. |
| **Agent** | Follow **`.cursor/rules/orgwave-orchestrator.mdc`**: if prerequisites fail, **stop** with this gate; otherwise use **only** GitHub MCP tools for GitHub work. |

**Nothing in this repo enables a disabled server programmatically.** Toggle on, reload, new message.

### Listing caveat

**`search_repositories`** does not return **`permissions.push`** per row. Say so in the discovery table.

## Enabling a disabled MCP server

**Symptom:** Server appears under **Tools & MCP** but is **off** or **not running** — no tools reach the agent.

1. **Cursor Settings → Tools & MCP** → find the server by **`mcpServers.<id>`**.
2. **Enable** it; fix **env** if Cursor shows an error (**`mcp-servers/README.md`**).
3. **Developer: Reload Window** if tools still missing.
4. **Send a new message** so the agent receives tools.

**Agents:** For playbooks that require **`github`**, **stop** here until the user enables and reloads.

## GitHub MCP missing in Cursor

**Symptom:** No **`github`** entry or agent never sees GitHub tools.

**Cause:** Project MCP is read from **`.cursor/mcp.json` in the workspace root**. Opening a **parent** folder does not load **orgwave-playbooks**’s config.

**Fix:**

1. **File → Open Folder** → **`orgwave-playbooks`** directory.
2. **Developer: Reload Window**.
3. Confirm **`mcpServers.github`** in **`.cursor/mcp.json`**; if not, run **`python3 orgwave/scripts/build-mcp-json.py`** and reload.
4. Ensure a PAT reaches the MCP child (**`mcp-servers/README.md`**, **`github-mcp-launch.mjs`**).
