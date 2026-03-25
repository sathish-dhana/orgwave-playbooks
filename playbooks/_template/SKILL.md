---
name: orgwave-playbook-template
description: Template — copy folder to playbooks/<new-id>/ and register in orgwave/catalog.yaml.
---

# YOUR_PLAYBOOK_TITLE

## Prerequisites

Customize this section per playbook. The agent must satisfy it **before** discovery or edits.

- **MCP servers required:** List Cursor MCP server **ids** exactly as in `.cursor/mcp.json` → `mcpServers.<id>` (e.g. **`github`**). Add optional servers the same way (e.g. **`user-new-relic`**).
- **Enabled:** For each required id, confirm the server is **on** under **Cursor → Settings → Tools & MCP**. If a required server is **missing from the session** (no tools) or **disabled**, **stop** and tell the user how to fix it (enable toggle, **Developer: Reload Window**, send a new message). Do not substitute shell tools for steps this playbook binds to MCP unless the user explicitly opts out after seeing the gate.
- **Definition on disk:** If **Prerequisites** lists an id that is **not** in the workspace `.cursor/mcp.json`, **stop** and instruct: add **`mcp-servers/servers/<id>.json`** per **`mcp-servers/README.md`**, run **`python3 orgwave/scripts/build-mcp-json.py`**, commit **`.cursor/mcp.json`**, reload Cursor, then enable the server.
- **PAT / API tokens:** For **github**, the launcher **`orgwave/scripts/github-mcp-launch.mjs`** loads token-related vars from **`~/.zshrc`** when they are still unset, and merges **`github-mcp.env`** — see **`mcp-servers/README.md`**. Before relying on MCP, the agent should treat **401/403** after one retry as a hard stop with **`orgwave/required-mcp.md`** (and playbook-specific gate text). Other servers: document required env vars in this bullet (often `${env:VAR}` in the server JSON plus values in **`.env`** or the user shell).

## 1. Intent

- **Change:** …
- **Done when:** …

## 2. Repo eligibility

- Must have: …
- Must not: …
- Optional: name pattern, topics, language …

## 3. Discovery

Use **MCP** when available (see `mcp-servers/servers/` + `orgwave/required-mcp.md`), or `discovery-output.json` if the user provides it (e.g. from `orgwave/scripts/discover-repos.sh`). Apply **Eligibility**. Print a **numbered** table: `#`, repo, default branch, URL. **Stop** until the user picks repos.

**Org / scope:** …

## 4. Execution (per selected repo)

1. Local workspace path or clone; verify `git` remote.
2. Branch: `techtask/<playbook-id>-<short-slug>` from the repo **`default_branch`** (API / `gh repo view`). If branch or file ops **404**, retry ref **`master`** then **`main`**.
3. Apply changes; run tests/build as appropriate.
4. Conventional commit, push, **one PR** per repo.

## 5. PR

- **Title:** `PLAYBOOK_ID: short title`
- **Body:** summary, checklist, tests, rollback; **do not merge** without owners.

## 6. Checklist

- [ ] Scoped to this playbook only
- [ ] Tests/build where applicable
- [ ] No secrets or unrelated files

## Optional tooling

- **`playbooks/<id>/discovery.json`** — filters for **`orgwave/scripts/discover-repos.sh`** ([orgwave/docs/reference.md](../../orgwave/docs/reference.md)).
- **MCP** — add shared servers under **`mcp-servers/servers/`** ([mcp-servers/README.md](../../mcp-servers/README.md)), then **`python3 orgwave/scripts/build-mcp-json.py`**; do not paste server config into this playbook.
- **Run in Cursor** is **not** defined in `SKILL.md` — add the playbook to **`orgwave/catalog.yaml`**, then run `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs` to refresh [orgwave/docs/run-in-cursor.md](../../orgwave/docs/run-in-cursor.md) and **`README.md` in this folder** (GitHub shows the play badge on the playbook directory).
