---
name: orgwave-example-migration
description: Sample OrgWave playbook — discover via GitHub MCP, select repos, add a POC marker file, open PRs.
---

# Example migration (POC)

## 1. Intent

- **Change:** Add a small marker file to show the OrgWave flow.
- **Done when:** Each chosen repo has an open PR with that change.

## 2. Eligibility

- Same GitHub org / scope the user names; not archived.
- Exclude names containing `archived-` or `deprecated-` if you keep that policy.

## 3. Discovery

1. If the user attached **`discovery-output.json`** from **OrgWave — discover repos**, use it as candidates (respect **Eligibility**); re-query only if asked.
2. Else list repos (GitHub MCP / `gh`) for the org.
3. Numbered table: `#`, name, default branch, `html_url`. **Stop** for selection.

## 4. Execution

Per selected repo: prefer a local clone in the workspace; else clone with user approval.

- Branch: `techtask/example-migration-poc`
- Add or update **`ORGWAVE_PLAYBOOK.md`** at repo root: `Playbook: example-migration (POC)`
- Commit: `chore: add OrgWave playbook marker (POC)`; push; open PR.

## 5. PR

- **Title:** `example-migration: OrgWave POC marker`
- **Body:** Link this playbooks repo; POC only; **do not merge** without review.

## 6. Checklist

- [ ] User selected these repos explicitly
- [ ] One PR per service
- [ ] No merge by agent

## Actions (optional)

- **Discover:** `orgwave-discover.yml` + optional `discovery.json`
- **Scripted apply:** `orgwave-run.yml` + `scripts/gha-apply.sh` + `ORGWAVE_PAT`
- **Run in Cursor:** listed in `catalog.yaml` only; see [docs/run-in-cursor.md](../../docs/run-in-cursor.md) (auto-regenerated on `main`).
