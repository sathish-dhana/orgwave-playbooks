# OrgWave reference

## Run in Cursor (all playbooks)

Buttons for each entry in `catalog.yaml` live in **[run-in-cursor.md](run-in-cursor.md)**. After editing the catalog, run:

```bash
python3 scripts/generate-orgwave-deeplink.py --write-docs
```

---

## `discovery.json` (optional)

Place at `playbooks/<id>/discovery.json`. Used by **OrgWave — discover repos** and `scripts/discover-repos.sh`.

| Field | Type | Meaning |
|-------|------|---------|
| `archived` | boolean | Keep only repos whose `archived` flag matches this value (typically `false`). |
| `include_name_regex` | string or null | If set, `full_name` (`owner/repo`) must match (RE2-style; `jq` `test()`). |
| `exclude_name_regex` | string or null | If set, `full_name` must **not** match. |
| `require_topics_any` | string[] | If non-empty, repo must have **at least one** of these topic names. |

Omit the file to list all **non-archived** repos for the org (no extra filters).

## GitHub Actions

### Secret: `ORGWAVE_PAT`

Fine-grained or classic PAT with access to **target** repositories:

- **Discover / list:** read metadata (and repo list for the org).
- **Run playbook:** **contents** (write), **pull requests** (create), on each `owner/repo` you pass in.

If the secret is unset, Discover falls back to `GITHUB_TOKEN` (often enough for public repos or same-org visibility). **Run playbook** still requires `ORGWAVE_PAT` when `dry_run` is false.

### Workflow: OrgWave — discover repos

| Input | Description |
|-------|-------------|
| `organization` | Org or user login |
| `playbook_id` | Folder under `playbooks/` |

Outputs: **job summary** (markdown table) + artifact **`discovery-output`** (`discovery-output.json`).

### Workflow: OrgWave — run playbook

| Input | Description |
|-------|-------------|
| `playbook_id` | Must have `playbooks/<id>/scripts/gha-apply.sh` |
| `repositories` | `owner/repo`, comma or newline separated |
| `dry_run` | If true: clone + commit only; no push/PR |

The workflow sets **`ORGWAVE_BRANCH`** to `techtask/<playbook_id>-<run_id>`.

### `gha-apply.sh` environment

| Variable | Set by | Purpose |
|----------|--------|---------|
| `TARGET_REPO_DIR` | Workflow | Clone path |
| `REPO_SLUG` | Workflow | `owner/repo` |
| `DRY_RUN` | Workflow | `true` / `false` |
| `GH_TOKEN` | Workflow | Push + `gh pr create` |
| `ORGWAVE_BRANCH` | Workflow | Branch name to create/push |

Optional for PR body: `GITHUB_SERVER_URL`, `GITHUB_REPOSITORY`, `GITHUB_RUN_ID`.
