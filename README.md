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

---

## Maintainer / automation layout

| Path | Purpose |
|------|---------|
| **`orgwave/`** | Catalog, scripts, and generated docs (`catalog.yaml`, `scripts/`, `docs/`) |
| **`playbooks/`** | Playbook folders (`<id>/SKILL.md`, optional `discovery.json`) |
| **`.cursor/rules/`** | Cursor orchestrator rule (workspace root) |

Full detail: **[orgwave/docs/reference.md](orgwave/docs/reference.md)**.

## How to run

| Path | When to use |
|------|-------------|
| **Cursor Agent** | Real migrations: multi-file edits, judgment, tests. Open this repo, use the orchestrator rule, name a playbook from `orgwave/catalog.yaml`. |
| **Run in Cursor** (deeplink) | Same with a [prefilled prompt](https://cursor.com/docs/reference/deeplinks). **[All playbooks → orgwave/docs/run-in-cursor.md](orgwave/docs/run-in-cursor.md)** |

**Prerequisites:** Cursor with [GitHub MCP](https://cursor.com/docs) if you use the agent; **`gh`** and **`jq`** if you use [local discovery](orgwave/docs/reference.md#local-discovery-optional).

```bash
python3 orgwave/scripts/generate-orgwave-deeplink.py MY_PLAYBOOK_ID
python3 orgwave/scripts/generate-orgwave-deeplink.py MY_PLAYBOOK_ID --desktop
python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs
```

## Limits (by design)

- **github.com** does not run Cursor, MCP, or an LLM — execution is in **Cursor** (or your own tooling).
- **Deeplinks** prefill a prompt; [they do not auto-execute](https://cursor.com/docs/reference/deeplinks).
- **Do not merge** automated PRs without service-owner review unless your policy says otherwise.
