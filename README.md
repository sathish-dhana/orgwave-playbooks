# OrgWave playbooks

Central **playbook** definitions for org-wide tech changes: discover candidate GitHub repos, pick services, apply one playbook per run, open **one PR per service**.

## For playbook authors (usually all you need)

| What | Where |
|------|--------|
| Add or edit a playbook | **`playbooks/<id>/`** — copy from `playbooks/_template`, then edit `SKILL.md` |
| Register it | Add one row to **`orgwave/catalog.yaml`** (the `id` must match the folder name) |

That’s it. You do **not** add the green play button by hand.

**Play button:** After you change the catalog or generator, run from the **repo root**:

`python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`

That refreshes **`playbooks/<id>/README.md`** and **`orgwave/docs/run-in-cursor.md`** (commit those updates with your PR).

**MCP servers:** Top-level **`mcp-servers/`** — see **[mcp-servers/README.md](mcp-servers/README.md)**. After adding or editing **`mcp-servers/servers/*.json`**, run **`python3 orgwave/scripts/build-mcp-json.py`** and commit **`.cursor/mcp.json`**.

---

## Maintainer / automation layout

| Path | Purpose |
|------|---------|
| **`playbooks/`** | Playbook folders (`<id>/SKILL.md`, optional `discovery.json`) |
| **`mcp-servers/`** | MCP definitions (`servers/<id>.json`) → merged into `.cursor/mcp.json` — **[README](mcp-servers/README.md)** |
| **`orgwave/`** | Catalog, scripts, **[required-mcp.md](orgwave/required-mcp.md)** (MCP policy), generated docs |
| **`.cursor/rules/`** | Orchestrator rule |
| **`.cursor/mcp.json`** | **Generated** from `mcp-servers/servers/*.json` — run `orgwave/scripts/build-mcp-json.py` |

Full detail: **[orgwave/docs/reference.md](orgwave/docs/reference.md)**.

### Prerequisites — GitHub MCP (if you use it)

`mcp-servers/servers/github.json` maps **`GITHUB_PERSONAL_ACCESS_TOKEN`** ← **`${env:GITHUB_TOKEN}`** and also loads optional repo-root **`.env`**. Cursor only sees variables from your **shell environment** if Cursor was started with that environment (e.g. from Terminal).

**Recommended — `~/.zshrc` + launch Cursor from the terminal:**

```bash
# 1) Add once (replace the token; keep the line secret — do not commit)
echo 'export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"' >> ~/.zshrc

# 2) Load into the current shell
source ~/.zshrc

# 3) Start Cursor from this terminal so MCP inherits GITHUB_TOKEN (macOS Dock icon often does not)
open -a Cursor /path/to/orgwave-playbooks
```

**Optional — repo `.env` instead** (e.g. you always open Cursor from the Dock): copy **[`.env.example`](.env.example)** to **`.env`** at the repo root and set **`GITHUB_PERSONAL_ACCESS_TOKEN`**.

More detail: **[mcp-servers/README.md](mcp-servers/README.md)** · **`orgwave/required-mcp.md`**.

## How to run

**Workspace root:** Use **File → Open Folder** on the **`orgwave-playbooks`** directory itself. If you open a parent folder (e.g. a folder that contains many projects), Cursor will **not** load this repo’s **`.cursor/mcp.json`**, so **GitHub MCP** will not appear under **Tools & MCP**—see **[orgwave/required-mcp.md](orgwave/required-mcp.md)** (*GitHub MCP missing in Cursor*).

| Path | When to use |
|------|-------------|
| **Cursor Agent** | Real migrations: multi-file edits, judgment, tests. Open this repo, use the orchestrator rule, name a playbook from `orgwave/catalog.yaml`. |
| **Run in Cursor** (deeplink) | Same with a [prefilled prompt](https://cursor.com/docs/reference/deeplinks). **[All playbooks → orgwave/docs/run-in-cursor.md](orgwave/docs/run-in-cursor.md)** |

**Also:** **`gh`** and **`jq`** if you use [local discovery](orgwave/docs/reference.md#local-discovery-optional). For MCP, see **Prerequisites — GitHub MCP** above.

```bash
python3 orgwave/scripts/build-mcp-json.py
python3 orgwave/scripts/generate-orgwave-deeplink.py MY_PLAYBOOK_ID
python3 orgwave/scripts/generate-orgwave-deeplink.py MY_PLAYBOOK_ID --desktop
python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs
```

## Limits (by design)

- **github.com** does not run Cursor, MCP, or an LLM — execution is in **Cursor** (or your own tooling).
- **Deeplinks** prefill a prompt; [they do not auto-execute](https://cursor.com/docs/reference/deeplinks).
- **Do not merge** automated PRs without service-owner review unless your policy says otherwise.
