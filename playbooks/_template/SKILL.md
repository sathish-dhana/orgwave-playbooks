---
name: orgwave-playbook-template
description: Template — copy folder to playbooks/<new-id>/ and register in orgwave/catalog.yaml.
---

# YOUR_PLAYBOOK_TITLE

## 1. Intent

- **Change:** …
- **Done when:** …

## 2. Repo eligibility

- Must have: …
- Must not: …
- Optional: name pattern, topics, language …

## 3. Discovery

Use **global GitHub MCP** (or `discovery-output.json` if the user provides it — e.g. from `orgwave/scripts/discover-repos.sh`). Apply **Eligibility**. Print a **numbered** table: `#`, repo, default branch, URL. **Stop** until the user picks repos.

**Org / scope:** …

## 4. Execution (per selected repo)

1. Local workspace path or clone; verify `git` remote.
2. Branch: `techtask/<playbook-id>-<short-slug>` from default branch.
3. Apply changes; run tests/build as appropriate.
4. Conventional commit, push, **one PR** per repo.

## 5. PR

- **Title:** `PLAYBOOK_ID: short title`
- **Body:** summary, checklist, tests, rollback; **do not merge** without owners.

## 6. Checklist

- [ ] Scoped to this playbook only
- [ ] Tests/build where applicable
- [ ] No secrets or unrelated files

## Optional tooling

- **`playbooks/<id>/discovery.json`** — filters for **`orgwave/scripts/discover-repos.sh`** ([orgwave/docs/reference.md](../../orgwave/docs/reference.md)).
- **Run in Cursor** is **not** defined in `SKILL.md` — add the playbook to **`orgwave/catalog.yaml`**, then run `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs` to refresh [orgwave/docs/run-in-cursor.md](../../orgwave/docs/run-in-cursor.md) and **`README.md` in this folder** (GitHub shows the play badge on the playbook directory).
