# OrgWave reference

## Run in Cursor (all playbooks)

- **Source of truth:** `orgwave/catalog.yaml` only. Playbook folders do **not** contain button code.
- **Generated files:** [run-in-cursor.md](run-in-cursor.md) (all playbooks) and **`playbooks/<id>/README.md`** (per playbook — GitHub renders this under the folder file list so the play badge appears *in* `playbooks/my-playbook/`). Markup lives in `orgwave/scripts/generate-orgwave-deeplink.py` (`RUN_BUTTON_*`, `run_in_cursor_badge()`).
- **Regenerate (repo root):** `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs` — commit the updated `orgwave/docs/run-in-cursor.md` and `playbooks/<id>/README.md` files with your changes.

---

## MCP servers

- **Policy:** [`../required-mcp.md`](../required-mcp.md).
- **How to add servers:** [`../mcp/README.md`](../mcp/README.md) — one JSON file per server under [`../mcp/servers/`](../mcp/servers/).
- **Merge script:** `python3 orgwave/scripts/build-mcp-json.py` → writes [`.cursor/mcp.json`](../../.cursor/mcp.json) ([Cursor project MCP](https://cursor.com/docs/context/mcp)). Tokens only via `${env:…}` / `_orgwave.env`, never committed.
- **Agent behavior:** Prefer MCP when tools work; **never block** — fall back to `gh` / `discovery-output.json` per `required-mcp.md`.

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

## Local discovery (optional)

From the **repository root**, with **`gh`** authenticated (`GH_TOKEN` or `gh auth login`):

```bash
ORG=my-org PLAYBOOK_ID=my-playbook ./orgwave/scripts/discover-repos.sh
```

Writes **`discovery-output.json`** in the current directory by default (override with **`OUT_JSON`**). Use that file in Cursor as the candidate list, or paste the table into chat.

---

## New playbooks

Copy `playbooks/_template/`, register in **`orgwave/catalog.yaml`**, then run **`--write-docs`** so the play badge and index stay in sync. Do not hand-edit generated READMEs — see [run-in-cursor.md](run-in-cursor.md).
