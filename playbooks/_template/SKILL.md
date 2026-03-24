---
name: orgwave-playbook-template
description: Template only — copy folder to playbooks/<new-id>/ and register in catalog.yaml.
---

# YOUR_PLAYBOOK_TITLE

## 1. Intent

- **Change:** …
- **Done when:** …

## 2. Repo eligibility (valid services for this migration)

- Must have: …
- Must not: …
- Match (optional): name pattern, topic, language, archived=false …

## 3. Discovery (global GitHub MCP — do not configure MCP here)

1. Use the **globally enabled GitHub MCP** to list/search repositories per org rules below.
2. Apply **Eligibility**; drop repos that do not qualify.
3. Output a **numbered table**: `#`, repo name, default branch, URL, short note (e.g. build type if inferable).
4. **Stop** and ask: *Which numbers or repo names should I run?* Do not edit any repo until the user selects.

**Org / scope:** … (e.g. org slug, team, topic filter — fill when copying)

## 4. Execution (per user-selected repo)

For each selected service:

1. Resolve a **local path** (workspace clone) or clone if missing; confirm `git` remote matches GitHub.
2. Branch: `techtask/<playbook-id>-<short-slug>` from default branch.
3. Apply changes: … (files, patterns)
4. Run tests/build: …
5. Commit (conventional), push `origin`, create **one PR** per service.

## 5. PR

- **Title:** `PLAYBOOK_ID: short title`
- **Body:** summary, checklist, test commands, rollback note.
- **Do not merge.**

## 6. Checklist before push

- [ ] Only this playbook’s changes
- [ ] Build/tests executed
- [ ] No secrets or unrelated files
