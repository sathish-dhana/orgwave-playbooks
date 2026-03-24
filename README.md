# OrgWave playbooks

Git repo of **subagent playbooks**: each playbook lists valid services (via your globally enabled **GitHub MCP**), waits for you to pick services, then applies changes and opens **one PR per service**.

## Layout

| Path | Purpose |
|------|---------|
| `catalog.yaml` | Index of playbooks — **select** by `id` |
| `playbooks/<id>/SKILL.md` | Full workflow for that subagent |
| `playbooks/_template/SKILL.md` | Copy this to add a new playbook |
| `.cursor/rules/orgwave-orchestrator.mdc` | Tells Cursor how to load catalog + playbook |
| `.github/workflows/orgwave-run.yml` | **Actions:** scripted apply + PR (no Cursor) |
| `.github/workflows/orgwave-discover.yml` | **Actions:** list repos via GitHub API → artifact for Cursor |
| `playbooks/<id>/discovery.json` | Optional filters for Discover (regex, topics) |
| `scripts/discover-repos.sh` | Same discovery locally: `ORG=… PLAYBOOK_ID=… ./scripts/discover-repos.sh` |
| `playbooks/<id>/scripts/gha-apply.sh` | Optional; required for scripted Actions apply |

## Quick start

1. Clone or copy this repo; open the folder in **Cursor**.
2. Enable **GitHub MCP** globally in Cursor (not inside each playbook).
3. **Attach the orchestrator rule** when you work: mention *OrgWave* or enable the rule for this workspace (see Cursor Rules).
4. In chat, trigger for example:

   - *“OrgWave: list playbooks”* then *“Run playbook `example-migration` for org `YOUR_ORG`”*
   - Or *“Run OrgWave playbook `example-migration`”*

5. When the agent shows the **numbered list** of valid repos, reply with the numbers or repo names to run.
6. The agent follows `playbooks/<id>/SKILL.md` and creates PRs.

## Add a new subagent

1. `cp -r playbooks/_template playbooks/my-new-migration`
2. Edit `playbooks/my-new-migration/SKILL.md` (intent, eligibility, discovery scope, execution, PR).
3. Add an entry under `playbooks:` in `catalog.yaml` with a unique `id`.
4. Commit and push; share the repo so others use the same playbooks.

## Recommended: Discover in Actions, apply in Cursor

You cannot attach **Cursor MCP** to a GitHub-hosted runner. The practical split:

1. **Actions → OrgWave — discover repos** — Uses `gh` + the same **GitHub API** your MCP would use. Produces a **job summary table** + artifact `discovery-output.json` (filtered by `playbooks/<id>/discovery.json` if present).
2. **Cursor → Agent + GitHub MCP** — You pick repos from that list (or paste JSON). The agent follows `SKILL.md`, edits locally, opens PRs with judgment for fuzzy migrations.

## GitHub Actions (scripted apply, optional)

Hosted runners **cannot** run Cursor or read `SKILL.md` as an LLM playbook. **OrgWave — run playbook** runs **bash** only.

1. Add repository secret **`ORGWAVE_PAT`**: PAT (or fine-grained token) with **contents** and **pull-requests** on every target repo (and **metadata** read). Prefer a bot account or GitHub App installation token.
2. Push this repo to GitHub.
3. **Actions → OrgWave — run playbook → Run workflow**  
   - **playbook_id:** e.g. `example-migration`  
   - **repositories:** `my-org/service-a,my-org/service-b` (or one per line in the multiline field)  
   - **dry_run:** clone + commit locally in the runner only (no push/PR); use `false` for real PRs.

Each playbook that supports Actions must implement `playbooks/<id>/scripts/gha-apply.sh` (see `example-migration`). The workflow passes `ORGWAVE_BRANCH` (unique per run) so pushes do not collide.

## Notes

- **Selection** in Cursor happens in chat after discovery; **selection in Actions** is the `repositories` workflow input (you type/paste `owner/repo` list).
- **Local clones:** Prefer services already in your workspace; the playbook should say when to clone.
- **Merges:** Playbooks should say *do not merge*; owners approve in GitHub.
