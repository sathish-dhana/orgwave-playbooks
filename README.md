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
| `scripts/generate-orgwave-deeplink.py` | Build **Run in Cursor** `https://cursor.com/link/prompt?…` for a playbook id |
| `playbooks/<id>/scripts/gha-apply.sh` | Optional; required for scripted Actions apply |

## “Play button” from GitHub → Cursor (deeplink)

GitHub **cannot** run the Cursor agent, use MCP, or push PRs by itself. What you *can* do is a **one-click handoff**: a link that opens **Cursor with a prompt already filled in**. The user still **reviews and confirms** before anything runs ([Cursor deeplinks](https://cursor.com/docs/reference/deeplinks) never auto-execute).

**Typical flow**

1. On GitHub, open this README (or your fork) and click **Run in Cursor** below (or generate a link for another playbook).
2. Cursor opens; **open/clone `orgwave-playbooks` as the workspace** if it is not already (the deeplink does not clone for you).
3. Submit the prefilled prompt → Agent uses **GitHub MCP** + `SKILL.md` → you select services → it edits, pushes, opens PRs.

**Example playbook — Run in Cursor**

[![Run in Cursor](https://img.shields.io/badge/Run%20in-Cursor-111111?style=for-the-badge)](https://cursor.com/link/prompt?text=You+are+running+OrgWave.+Open+this+orgwave-playbooks+repository+as+the+Cursor+workspace+%28clone+it+first+if+needed%29.%0A%0A1.+Follow+.cursor%2Frules%2Forgwave-orchestrator.mdc+and+load+playbook+id+%60example-migration%60+from+catalog.yaml+and+playbooks%2Fexample-migration%2FSKILL.md.%0A2.+Ask+me+for+the+GitHub+org+if+unknown.+Use+global+GitHub+MCP+to+list%2Ffilter+repos+per+the+playbook+%28or+use+a+discovery+JSON+file+from+the+latest+Actions+run+if+I+attach+it%29.%0A3.+Show+a+numbered+table+of+candidate+services+and+STOP+until+I+select+which+repos+to+run.%0A4.+For+each+selected+service%3A+apply+the+playbook%2C+run+tests+if+applicable%2C+push+branches%2C+open+one+PR+per+service.+Do+not+merge.)

Generate links for other playbooks (web URL, safe for GitHub markdown):

```bash
python3 scripts/generate-orgwave-deeplink.py YOUR_PLAYBOOK_ID
python3 scripts/generate-orgwave-deeplink.py YOUR_PLAYBOOK_ID --desktop   # cursor://… for local sharing
```

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
4. Optional: add a **Run in Cursor** link to your README via `python3 scripts/generate-orgwave-deeplink.py <id>`.
5. Commit and push; share the repo so others use the same playbooks.

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
