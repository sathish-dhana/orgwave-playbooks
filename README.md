# OrgWave playbooks

Central **playbook** definitions for org-wide tech changes: discover candidate GitHub repos, pick services, apply one playbook per run, open **one PR per service**.  
**Cursor + GitHub MCP** handles fuzzy work; **GitHub Actions** can list repos (discover) or run **scripted** applies.

## Prerequisites

- **Cursor** with [GitHub MCP](https://cursor.com/docs) enabled globally (not per-playbook).
- **`gh`** and **`jq`** on your machine if you run discovery locally or extend scripts.
- For Actions on private repos: repository secret **`ORGWAVE_PAT`** (see [docs/reference.md](docs/reference.md)).

## How to run (pick one)

| Path | When to use |
|------|-------------|
| **Cursor Agent** | Real migrations: multi-file edits, judgment, tests. Open this repo, use the orchestrator rule, name a playbook from `catalog.yaml`. |
| **Run in Cursor** (deeplink) | Same as above, with a [prefilled prompt](https://cursor.com/docs/reference/deeplinks) from the button below. You still confirm before the agent runs. |
| **Actions → Discover** | Batch list repos via GitHub API → job summary + `discovery-output.json` artifact → continue in Cursor. |
| **Actions → Run playbook** | Deterministic shell only: `playbooks/<id>/scripts/gha-apply.sh`. No Cursor / no LLM. |

[![Run in Cursor — example-migration](https://img.shields.io/badge/Run_in-Cursor-111111?style=for-the-badge)](https://cursor.com/link/prompt?text=You+are+running+OrgWave.+Open+this+orgwave-playbooks+repository+as+the+Cursor+workspace+%28clone+it+first+if+needed%29.%0A%0A1.+Follow+.cursor%2Frules%2Forgwave-orchestrator.mdc+and+load+playbook+id+%60example-migration%60+from+catalog.yaml+and+playbooks%2Fexample-migration%2FSKILL.md.%0A2.+Ask+me+for+the+GitHub+org+if+unknown.+Use+global+GitHub+MCP+to+list%2Ffilter+repos+per+the+playbook+%28or+use+a+discovery+JSON+file+from+the+latest+Actions+run+if+I+attach+it%29.%0A3.+Show+a+numbered+table+of+candidate+services+and+STOP+until+I+select+which+repos+to+run.%0A4.+For+each+selected+service%3A+apply+the+playbook%2C+run+tests+if+applicable%2C+push+branches%2C+open+one+PR+per+service.+Do+not+merge.)

```bash
python3 scripts/generate-orgwave-deeplink.py YOUR_PLAYBOOK_ID        # https://cursor.com/link/…
python3 scripts/generate-orgwave-deeplink.py YOUR_PLAYBOOK_ID --desktop  # cursor://…
```

## Repository layout

| Path | Purpose |
|------|---------|
| `catalog.yaml` | Playbook index (`id`, `name`, `description`) |
| `playbooks/<id>/SKILL.md` | Instructions for Cursor Agent (intent, eligibility, discovery, execution, PR) |
| `playbooks/<id>/discovery.json` | Optional filters for Discover workflow / `discover-repos.sh` |
| `playbooks/<id>/scripts/gha-apply.sh` | Optional; required for **Actions → Run playbook** |
| `.cursor/rules/orgwave-orchestrator.mdc` | Loads catalog + playbook; enforces discover → select → PR |
| `.github/workflows/orgwave-discover.yml` | Manual discover run |
| `.github/workflows/orgwave-run.yml` | Manual scripted apply per repo list |
| `scripts/discover-repos.sh` | Local discover: `ORG=my-org PLAYBOOK_ID=my-playbook ./scripts/discover-repos.sh` |
| `scripts/generate-orgwave-deeplink.py` | Build “Run in Cursor” URLs |

## Add a playbook

1. `cp -r playbooks/_template playbooks/<id>`
2. Edit `playbooks/<id>/SKILL.md` and add a row to `catalog.yaml`.
3. Optional: `discovery.json`, `scripts/gha-apply.sh`, and a deeplink in your fork’s README (`generate-orgwave-deeplink.py`).

Details: **[docs/reference.md](docs/reference.md)**.

## Limits (by design)

- **GitHub** cannot run Cursor, MCP, or an LLM. Actions uses the **API** or **bash** only.
- **Deeplinks** prefill a prompt; [they do not auto-execute](https://cursor.com/docs/reference/deeplinks).
- **Do not merge** automated PRs without service-owner review unless your policy says otherwise.
