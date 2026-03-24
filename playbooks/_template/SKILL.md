---
name: orgwave-playbook-template
description: Template — copy folder to playbooks/<new-id>/ and register in catalog.yaml.
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

Use **global GitHub MCP** (or `discovery-output.json` from Actions if the user provides it). Apply **Eligibility**. Print a **numbered** table: `#`, repo, default branch, URL. **Stop** until the user picks repos.

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

## Optional automation

- **`playbooks/<id>/discovery.json`** — filters for Discover workflow / `scripts/discover-repos.sh` ([docs/reference.md](../../docs/reference.md)).
- **`playbooks/<id>/scripts/gha-apply.sh`** — deterministic apply for **Actions → Run playbook** (no Cursor).
