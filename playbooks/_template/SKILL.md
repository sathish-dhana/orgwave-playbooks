---
name: orgwave-playbook-template
description: Template — copy folder to playbooks/<new-id>/ and register in orgwave/catalog.yaml.
---

# YOUR_PLAYBOOK_TITLE

## Prerequisites

Customize this section per playbook. The agent must satisfy it **before** discovery or edits.

- **MCP servers required:** List Cursor MCP server **ids** exactly as in `.cursor/mcp.json` → `mcpServers.<id>` (e.g. **`github`**). Add optional servers the same way (e.g. **`user-new-relic`**). In **`orgwave/catalog.yaml`**, set **`mcp_install:`** to the same id(s) (comma-separated) so the generated **`README.md`** gets a blue **Add to Cursor** button ([Cursor MCP install links](https://cursor.com/docs/context/mcp/install-links)).
- **Hard stop:** If a required **`id`** is **missing** from **`.cursor/mcp.json`**, **stop** — add **`mcp-servers/servers/<id>.json`**, run **`python3 orgwave/scripts/build-mcp-json.py`**, reload, enable the server (**`orgwave/required-mcp.md`**).
- **Hard stop:** If a required server is **disabled** or its tools **do not attach** to the session, **stop** with enable + reload steps — **do not** substitute shell or REST for that server’s work.
- **Hard stop:** **401** / **403** from that server after one retry → **stop** with PAT / env guidance (**`mcp-servers/README.md`**, **`orgwave/required-mcp.md`**).
- **PAT / API tokens:** For **`github`**, see **`orgwave/scripts/github-mcp-launch.mjs`** and **`mcp-servers/README.md`**. Other servers: document required env vars here.

When every prerequisite passes, **continue**.

## 1. Intent

- **Change:** …
- **Done when:** …

## 2. Repo eligibility

- Must have: …
- Must not: …
- Optional: name pattern, topics, language …

## 3. Discovery

Use **only** the MCP tools listed in **Prerequisites** (e.g. GitHub **`search_repositories`**). Apply **Eligibility**. Print a **numbered** table: `#`, repo, default branch when present, URL. **Stop** until the user picks repos.

**Org / scope:** …

## 4. Execution (per selected repo)

1. Use MCP tools from **Prerequisites** for branches, files, and pushes (no **`gh`** / **`git`** / ad-hoc REST unless this playbook explicitly lists none and you document an exception — default is **MCP only**).
2. Branch: `techtask/<playbook-id>-<short-slug>` from the repo **default branch** (from MCP). If operations **404**, retry ref **`master`** then **`main`**.
3. Apply changes; run tests/build as appropriate.
4. **One PR** per repo via MCP **`create_pull_request`** (or the PR tool your server exposes).

## 5. PR

- **Title:** `PLAYBOOK_ID: short title`
- **Body:** summary, checklist, tests, rollback; **do not merge** without owners.

## 6. Checklist

- [ ] Scoped to this playbook only
- [ ] Tests/build where applicable
- [ ] No secrets or unrelated files
- [ ] MCP prerequisites satisfied or run **stopped** with gate

## Optional tooling

- **`playbooks/<id>/discovery.json`** — filters for **`orgwave/scripts/discover-repos.sh`** ([orgwave/docs/reference.md](../../orgwave/docs/reference.md)); does **not** replace MCP when the playbook requires **`github`**.
- **MCP** — add shared servers under **`mcp-servers/servers/`** ([mcp-servers/README.md](../../mcp-servers/README.md)), then **`python3 orgwave/scripts/build-mcp-json.py`**; do not paste server config into this playbook.
- **Run in Cursor** — add the playbook to **`orgwave/catalog.yaml`**, then run `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs` to refresh [orgwave/docs/run-in-cursor.md](../../orgwave/docs/run-in-cursor.md) and **`README.md`** in this folder.
