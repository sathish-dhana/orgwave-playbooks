# MCP servers for OrgWave

This file is the **policy** for how the agent uses MCP. **Machine definitions** live in the top-level **`mcp-servers/`** folder (see below).

## Policy: general vs GitHub MCP gate

- **General:** Other servers and playbooks that do **not** bind discovery/PRs to GitHub MCP may still use **`gh`**, REST, or **`discovery-output.json`** when MCP is awkward or missing — see each **`playbooks/<id>/SKILL.md`**.
- **GitHub MCP gate (listing + PR):** Playbooks such as **`readme-cursor-smoke-test`** **require** GitHub MCP **`search_repositories`** for discovery and **`create_pull_request`** for opening PRs **when** those tools exist in the agent session. If GitHub MCP tools are **missing**, **disabled**, or return **auth errors** after a retry, the agent **stops** and sends the **checklist below** (workspace, enable server, PAT, reload). It **does not** substitute **`gh api user/repos`** or **`gh pr create`** in the same turn unless the user **explicitly** opts out after seeing the gate (e.g. “continue without MCP”).
- **`mcp-servers/servers/*.json`** describe each server; **`python3 orgwave/scripts/build-mcp-json.py`** merges them into **`.cursor/mcp.json`**, which Cursor loads. When env tokens are visible to Cursor, those servers **can** auto-start.
- The usual **stop** for repo selection (after the numbered table) still applies — that is separate from the MCP gate.

## Where things live

| Path | Role |
|------|------|
| **`mcp-servers/README.md`** | **How to add a server** — filename, JSON shape, `_orgwave` metadata, `${env:…}` secrets. |
| **`mcp-servers/servers/<id>.json`** | **Source of truth** per MCP server (one file per `<id>`). |
| **`orgwave/scripts/build-mcp-json.py`** | Merges `servers/*.json` → **`.cursor/mcp.json`**. Run after adding/editing server files. |
| **`.cursor/mcp.json`** | **Generated** — Cursor’s project MCP file ([docs](https://cursor.com/docs/context/mcp)). Commit it after running the script. |
| **`orgwave/required-mcp.md`** (this file) | **Behaviour** — MCP gate, fallbacks, auto-run notes. |

## What can be automated?

**Partly yes:** `.cursor/mcp.json` tells Cursor **which commands/URLs** to run for each server. **`${env:VAR}`** pulls tokens from the environment — no secrets in git.

| Step | Why |
|------|-----|
| **Secrets** | **GitHub:** **`github-mcp-launch.mjs`** sets the PAT: **`GITHUB_PERSONAL_ACCESS_TOKEN`** from **`.env`** wins if set; otherwise (by default) **`gh auth token`** before **`GITHUB_TOKEN`** / **`GH_TOKEN`** so MCP matches terminal **`gh`**. **`github-mcp.env`** and **`.zshrc`** merge into **empty** keys only. **`ORGWAVE_MCP_PREFER_ENV_TOKEN=1`** forces env tokens before **`gh`**. See **`mcp-servers/README.md`**. Deeplinks cannot inject tokens. |
| **Pinned GitHub MCP** | Once per clone: **`cd orgwave/mcp-runtime && npm ci`** so the launcher spawns the pinned server with **`node`** (fast). Without it, **`npx`** cold starts may be slow enough that Cursor shows **empty offerings** / **Client closed** until retry. |
| **Reload** | After changing **`mcp.json`**, reload Cursor or restart if tools do not appear. |
| **Tool approval** | Cursor may prompt per tool; for **GitHub MCP gate** playbooks, retry once then **gate message** — not silent **`gh`** listing/PR unless the user opts out. |
| **Enable server** | If a server is **listed but disabled**, turn it **on** in Cursor (see **Enabling a disabled MCP server** below) so tools reach the agent. |

### If you already set tokens — is it “auto”?

When repo **`.env`**, **`~/.cursor/github-mcp.env`**, tokens from **`~/.zshrc`** (via launcher source), **`GITHUB_TOKEN`**, **`GH_TOKEN`**, or **`gh auth token`** (after **`gh auth login`**, with Homebrew on **`PATH`**) reaches the MCP child, GitHub MCP can authenticate. The macOS **Dock** icon and **Run in Cursor** from GitHub often do **not** load **`~/.zshrc`** into Cursor’s GUI — the launcher still **sources** **`~/.zshrc`** for the GitHub MCP child when needed; alternatively use **`.env`**, **`~/.cursor/github-mcp.env`**, or **`open -a Cursor …`** from a shell that exports the token.

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
- For **GitHub MCP gate** playbooks, **`gh`** / **`discovery-output.json`** are fallbacks **only** after the user confirms MCP cannot be used or has fixed setup and asked to continue with an alternate path.

## GitHub MCP gate — checklist for the agent to paste when tools are missing or auth fails

1. **Workspace:** **File → Open Folder** → the **`orgwave-playbooks`** repo root (folder containing **`orgwave/catalog.yaml`** and **`.cursor/mcp.json`**), not a parent monorepo tree.
2. **Enable server:** **Cursor Settings → Tools & MCP** → turn **on** the **`github`** server (same id as **`mcpServers.github`**).
3. **PAT:** Set a valid token so the MCP child receives it — see **`mcp-servers/README.md`**: repo **`.env`** **`GITHUB_PERSONAL_ACCESS_TOKEN`**, or **`~/.cursor/github-mcp.env`**, or **`gh auth login`** (launcher prefers **`gh auth token`** by default). Fix **401** vs **403** per the README table.
4. **Reload:** **Command Palette → Developer: Reload Window**, then **send a new message** so GitHub tools attach to the session.
5. **Optional:** **`cd orgwave/mcp-runtime && npm ci`** for a fast pinned GitHub MCP server.

After this, the agent should use **`search_repositories`** and **`create_pull_request`** again — not **`gh`** for those steps when MCP works.

## Changing MCP servers

1. Add or edit **`mcp-servers/servers/<id>.json`** (see **`mcp-servers/README.md`**).
2. Run **`python3 orgwave/scripts/build-mcp-json.py`** and commit **`.cursor/mcp.json`**.
3. Update **`orgwave/required-mcp.md`** tables if the default set changes.
4. If deeplink wording must change, edit **`build_prompt()`** in `orgwave/scripts/generate-orgwave-deeplink.py` and run **`python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`**.

## Making the agent actually use GitHub MCP

**Agents only “see” MCP tools that Cursor attaches to the current chat.** Settings can show **github** as on while a run still used the shell—that usually means the model chose REST/`gh`, or that turn had no MCP tool calls. To steer behavior:

| Who | What to do |
|-----|------------|
| **You (user)** | Workspace = **orgwave-playbooks** root; **Tools & MCP** → **github** **on**; **Developer: Reload Window** after toggling or editing **`mcp.json`**. |
| **You (user)** | Approve GitHub tool prompts when asked, or add allowlist patterns (e.g. **`github:*`**) via Cursor permissions docs — see **`mcp-servers/README.md`**. |
| **Agent** | Follow **`.cursor/rules/orgwave-orchestrator.mdc`**: **MCP-first** for listing/PR on gate playbooks; use **`gh`** / REST for clone/push and for discovery/PR **only** when MCP tools are absent after the gate or the user opts out. |

**Important:** Nothing in this repo can **programmatically enable** a disabled MCP server. **You** flip the toggle; then **reload**; the **next** agent turn gets the tools.

### Push verification vs MCP listing

**`search_repositories`** does not return **`permissions.push`** per row. The numbered table must **say so**. If the user **explicitly** wants push-verified rows **in addition to** the MCP list, the agent may run **`gh api user/repos`** or REST and annotate — but **not** **instead of** MCP **`search_repositories`** when the playbook requires MCP discovery and tools exist.

### GitHub CLI (`gh`) missing in the agent shell

- **Often:** `gh` is not installed — install with **`brew install gh`** on macOS when Homebrew is present (agent may request network to run it).
- **Or:** `gh` is installed under Homebrew but the agent’s **PATH** omits **`/opt/homebrew/bin`** or **`/usr/local/bin`** — use the full path to `gh` or export PATH for that command.
- **Still use GitHub MCP** for file/branch/PR steps when tools exist in the session; use **`gh api …`** or REST for push-filtered repo lists when the playbook requires it.

## Enabling a disabled MCP server

**Symptom:** The server **appears** under **Cursor Settings → Tools & MCP** (names may vary slightly by Cursor version), but it is **off**, **disabled**, or **not running** — so the agent gets **no tools** from that server even though **`mcp-servers/servers/<id>.json`** and **`.cursor/mcp.json`** are correct.

**Do this:**

1. Open **Cursor Settings** → **Tools & MCP** (or the MCP section in **Features**).
2. Find the server by its **id** — the same key as in **`.cursor/mcp.json`** under **`mcpServers`** (e.g. **`github`** for GitHub). Project servers from **orgwave-playbooks** only load when the workspace folder is this repo root (see *GitHub MCP missing in Cursor*).
3. **Enable** / turn **on** the server. If Cursor shows an error, fix **env vars** (see **`mcp-servers/README.md`** and the **`_orgwave.env`** list in that server’s JSON) and try again.
4. **Command Palette → Developer: Reload Window** if tools still do not show for the agent.
5. **Send a new message** to the agent (or continue the thread after reload) so it can use GitHub tools on that run.

**For agents:** For **GitHub MCP gate** playbooks, if the server was disabled or tools are missing, point them here and **stop** until they enable and reload (or **explicitly** opt out). For other playbooks, you may continue with **`gh`** / REST after giving these steps.

## GitHub MCP missing in Cursor

**Symptom:** **Tools & MCP** lists other servers (e.g. Grafana, New Relic) but **no `github`** entry, or the agent never sees GitHub MCP tools.

**Cause:** Cursor reads **project** MCP from **`.cursor/mcp.json` in the workspace root**. Running OrgWave with the workspace opened on a **parent folder** (multi-project tree, monorepo root, or `IdeaProjects`) does **not** load **orgwave-playbooks**’s `.cursor/mcp.json`, so **GitHub MCP is never started**. Playbooks also **cannot** create that connection at runtime—it is configuration, not something the agent registers by following `SKILL.md`.

**Fix:**

1. **File → Open Folder** and choose the **`orgwave-playbooks`** directory itself (the folder that contains **`orgwave/catalog.yaml`** and **`.cursor/mcp.json`**).
2. **Command Palette → Developer: Reload Window** (or restart Cursor).
3. Confirm **`.cursor/mcp.json`** contains **`mcpServers.github`**; if not, from repo root run **`python3 orgwave/scripts/build-mcp-json.py`** and reload again.
4. Ensure a PAT reaches GitHub MCP: **`GITHUB_TOKEN`** / **`GH_TOKEN`** in the Cursor process, repo **`.env`** **`GITHUB_PERSONAL_ACCESS_TOKEN`**, or **`gh auth login`** (see **`mcp-servers/README.md`** and **`orgwave/scripts/github-mcp-launch.mjs`**).

After that, **github** should appear alongside any **user-level** MCP servers. If **github** is listed but **disabled**, use **Enabling a disabled MCP server** above. For **GitHub MCP gate** playbooks, **do not** fall back to **`gh`** for listing/PR until the user opts out — use the **GitHub MCP gate** checklist instead.
