---
name: orgwave-readme-cursor-smoke-test
description: Test playbook — GitHub MCP (or gh), list repos you can push to, select targets, append one line to README.md via PR.
---

# README Cursor smoke test

## 1. Intent

- **Change:** Append a single line to **`README.md`** at the repo root of each selected service: **`Updated by Cursor.`** (on its own line at the end of the file).
- **Done when:** Each chosen repo has an **open PR** with that README change. **Do not merge** unless the user asks.

## 2. Eligibility

- Repositories where the **authenticated user/token has `push`** (write) access — not read-only.
- **Not** archived.
- **Skip** if there is no `README.md` **and** the user does not want one created; otherwise **create** `README.md` with at least a title line plus **`Updated by Cursor.`** on the last line.

## 3. Discovery

0. **MCP scope:** GitHub MCP is **not** started by this playbook. Cursor only loads it from **`.cursor/mcp.json`** when the **workspace root** is the **orgwave-playbooks** repo folder. If the user opened a parent directory, **Tools & MCP** may show only global/other servers—point them to **`orgwave/required-mcp.md`** (*GitHub MCP missing in Cursor*) and use **`gh`** or GitHub REST API + **`GITHUB_TOKEN`**; do not block.
1. **MCP-first (orchestrator):** If GitHub MCP tools exist **in this chat session**, use them where they match the operation (e.g. **`search_repositories`** for discovery). **Do not** duplicate the same GitHub call via shell when MCP can do it. The agent **cannot** enable a disabled server—if **github** is off, tell the user to enable it and **Developer: Reload Window** per **`orgwave/required-mcp.md`** (*Enabling a disabled MCP server*, *Making the agent actually use GitHub MCP*).
2. **List repositories** the token can **push** to, for the scope the user names (their user account, specific org(s), or “all my repos”):
   - **Push-accurate list:** `@modelcontextprotocol/server-github` has no **`GET /user/repos`-style** tool with **`permissions.push`**. Use **`gh api user/repos --paginate`** (filter `.permissions.push == true`) or **REST + token** for that requirement.
   - **MCP-only discovery (approximate):** e.g. **`search_repositories`** with `user:<login>` (paginate); then **note** if push metadata was not verified, or follow with REST for the final push-filtered table.
3. Print a **numbered** table: `#`, `full_name`, default branch, `html_url`, and a short note **push: yes** (or omit non-push).
4. **Stop** until the user selects repos (numbers, `owner/repo` list, or “all in table”).

## 4. Execution

Per **selected** repo (clone into workspace or temp path; respect user preference):

1. Default branch: use repo’s default (from API / `gh repo view`).
2. Branch name: **`techtask/readme-cursor-smoke-test`** (from latest default).
3. **`README.md`:**
   - If it exists: ensure file ends with a newline, then append exactly: **`Updated by Cursor.`** on a new final line (no duplicate if that exact line already exists as the last line — skip or warn).
   - If it does not exist: create **`README.md`** with a one-line title (e.g. `# <repo name>`) and then **`Updated by Cursor.`** on the last line.
4. Commit: **`chore: append OrgWave smoke-test line to README`**
5. Push branch; open **one PR** per repo to default branch.

## 5. PR

- **Title:** `readme-cursor-smoke-test: README smoke test (OrgWave)`
- **Body:** Short explanation; link this **orgwave-playbooks** repo and playbook id **`readme-cursor-smoke-test`**; **do not merge** without owner review.

## 6. Checklist

- [ ] Only repos with **push** access were listed and changed
- [ ] User explicitly selected targets
- [ ] One PR per repo; agent did **not** merge

## Automation notes

- **Catalog / Run in Cursor:** `orgwave/catalog.yaml` — regenerate UI with `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`.
- **MCP / `.zshrc`:** [mcp-servers/README.md](../../mcp-servers/README.md), [orgwave/required-mcp.md](../../orgwave/required-mcp.md).
