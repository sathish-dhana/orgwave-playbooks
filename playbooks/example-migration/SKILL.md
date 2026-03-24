---
name: orgwave-example-migration
description: Example OrgWave playbook — lists eligible repos via global GitHub MCP, waits for selection, then opens PRs. Replace eligibility and execution for a real task.
---

# Example migration

## 1. Intent

- **Change:** Demonstrate the OrgWave flow (no real production change unless you extend this file).
- **Done when:** User-selected repos have a trivial doc-only or agreed change and an open PR.

## 2. Repo eligibility

- **Must:** Be under the GitHub org / scope defined in section 3; not archived.
- **Must not:** Name contains `archived-` or `deprecated-` (adjust to taste).

## 3. Discovery (global GitHub MCP)

1. If the user already ran **GitHub Actions → OrgWave — discover repos** (or attached `discovery-output.json`), treat that list as candidates matching **Eligibility**; only re-query GitHub if they ask to refresh.
2. Otherwise: list repositories for the org the user names (ask once if missing): e.g. `my-org`, using GitHub MCP / `gh`.
3. Filter with **Eligibility** (and align with `discovery.json` when Actions was used).
4. Print numbered table: `#`, name, default branch, `html_url`.
5. **Stop** for user selection (numbers or full names).

## 4. Execution (per selected repo)

1. Use local checkout under the user workspace if present; otherwise clone to a path the user approves.
2. Branch: `techtask/example-migration-poc`.
3. **Minimal safe change for POC:** add or update `ORGWAVE_PLAYBOOK.md` at repo root with one line: `Playbook: example-migration (POC)`.
4. Run `git status`; if the repo has a standard build, run its quick check only if appropriate (skip if unknown).
5. Commit: `chore: add OrgWave playbook marker (POC)`, push, open PR.

## 5. PR

- **Title:** `example-migration: OrgWave POC marker`
- **Body:** Link to `orgwave-playbooks` repo; note this is a POC; do not merge without review.

## 6. Checklist

- [ ] User explicitly selected these repos
- [ ] One PR per service
- [ ] No merge

## 7. GitHub Actions

- **Discover:** workflow **OrgWave — discover repos** writes `discovery-output.json` + job summary (GitHub API only). Optional filters: `discovery.json`.
- **Apply without Cursor:** workflow **OrgWave — run playbook** + `repositories` input and `scripts/gha-apply.sh` (secret `ORGWAVE_PAT`; branch from `ORGWAVE_BRANCH`).
