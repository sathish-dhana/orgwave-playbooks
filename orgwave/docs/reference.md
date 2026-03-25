# OrgWave reference

## Run in Cursor (all playbooks)

- **Source of truth:** `orgwave/catalog.yaml` only. Playbook folders do **not** contain button code.
- **Generated files:** [run-in-cursor.md](run-in-cursor.md) (all playbooks) and **`playbooks/<id>/README.md`** (per playbook — GitHub renders this under the folder file list so the play badge appears *in* `playbooks/my-playbook/`). Markup lives in `orgwave/scripts/generate-orgwave-deeplink.py` (`RUN_BUTTON_*`, `run_in_cursor_badge()`, MCP install helpers).
- **Optional `mcp_install`:** Comma-separated MCP server ids (`mcp-servers/servers/<id>.json`). Drives blue **Add to Cursor** buttons using [Cursor MCP install deeplinks](https://cursor.com/docs/context/mcp/install-links) (`cursor://anysphere.cursor-deeplink/mcp/install?...`). Keep in sync with **`MCP servers required`** in each playbook’s **`SKILL.md`**.
- **Regenerate (repo root):** `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs` — commit the updated `orgwave/docs/run-in-cursor.md` and `playbooks/<id>/README.md` files with your changes.
- **Debug one install URL:** `python3 orgwave/scripts/generate-orgwave-deeplink.py --mcp-install github`

---

## MCP servers

- **Policy:** [`../required-mcp.md`](../required-mcp.md).
- **How to add servers:** [`../../mcp-servers/README.md`](../../mcp-servers/README.md) — one JSON file per server under [`../../mcp-servers/servers/`](../../mcp-servers/servers/).
- **Merge script:** `python3 orgwave/scripts/build-mcp-json.py` → writes [`.cursor/mcp.json`](../../.cursor/mcp.json) ([Cursor project MCP](https://cursor.com/docs/context/mcp)). **GitHub:** `GITHUB_TOKEN` in **`~/.zshrc`** + launch Cursor from terminal, or optional [`.env`](../../.env.example) — never commit secrets.
- **Agent behavior:** If a playbook **requires** an MCP server, use **only** that server’s tools for those steps; if prerequisites fail (**missing `mcp.json` entry**, **disabled**, **no tools in session**, **401/403** after retry), **stop** with `required-mcp.md` — **no** `gh` / REST substitute.
- **Disabled in UI:** If a server is listed under Tools & MCP but **off**, enable it per [`required-mcp.md` → *Enabling a disabled MCP server*](../required-mcp.md#enabling-a-disabled-mcp-server).

---

## `discovery.json` (optional)

Place at `playbooks/<id>/discovery.json`. Used by **`orgwave/scripts/discover-repos.sh`** when listing repos for that playbook.

| Field | Type | Meaning |
|-------|------|---------|
| `archived` | boolean | Keep only repos whose `archived` flag matches this value (typically `false`). |
| `include_name_regex` | string or null | If set, `full_name` (`owner/repo`) must match (RE2-style; `jq` `test()`). |
| `exclude_name_regex` | string or null | If set, `full_name` must **not** match. |
| `require_topics_any` | string[] | If non-empty, repo must have **at least one** of these topic names. |

Omit the file to list all **non-archived** repos for the org (no extra filters).

## Local discovery (optional, human / attachment only)

From the **repository root**, with **`gh`** authenticated (for the script only):

```bash
ORG=my-org PLAYBOOK_ID=my-playbook ./orgwave/scripts/discover-repos.sh
```

Writes **`discovery-output.json`** by default (override with **`OUT_JSON`**). You may attach it for context; playbooks that **require** GitHub MCP still expect in-session **`search_repositories`** (or the agent **stops** at the gate — the script does **not** replace MCP).

---

## New playbooks

Copy `playbooks/_template/`, register in **`orgwave/catalog.yaml`**, then run **`--write-docs`** so the play badge and index stay in sync. Do not hand-edit generated READMEs — see [run-in-cursor.md](run-in-cursor.md).
