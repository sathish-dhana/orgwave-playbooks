# OrgWave playbooks

Git repo of **subagent playbooks**: each playbook lists valid services (via your globally enabled **GitHub MCP**), waits for you to pick services, then applies changes and opens **one PR per service**.

## Layout

| Path | Purpose |
|------|---------|
| `catalog.yaml` | Index of playbooks — **select** by `id` |
| `playbooks/<id>/SKILL.md` | Full workflow for that subagent |
| `playbooks/_template/SKILL.md` | Copy this to add a new playbook |
| `.cursor/rules/orgwave-orchestrator.mdc` | Tells Cursor how to load catalog + playbook |

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

## Notes

- **Selection** happens in chat after discovery — there is no separate UI; the catalog is the menu.
- **Local clones:** Prefer services already in your workspace; the playbook should say when to clone.
- **Merges:** Playbooks should say *do not merge*; owners approve in GitHub.
