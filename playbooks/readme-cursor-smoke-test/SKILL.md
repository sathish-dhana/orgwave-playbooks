---
name: orgwave-readme-cursor-smoke-test
description: Test playbook — GitHub MCP for repo listing and PR only; gh/git for clone, branch, README, push; then select targets.
---

# README Cursor smoke test

## 1. Intent

- **Change:** Append a single line to **`README.md`** at the repo root of each selected service: **`Updated by Cursor.`** (on its own line at the end of the file).
- **Done when:** Each chosen repo has an **open PR** with that README change. **Do not merge** unless the user asks.

## 2. Eligibility

- Repositories you intend to change should be ones the **same identity as GitHub MCP / `gh`** can **push** to (write). **`search_repositories`** does **not** return **`permissions.push`** per repo — state in the discovery table that rows are **MCP search candidates** (same token as MCP); exclude forks/archived if the search query supports it (`archived:false`, etc.).
- **Skip** if there is no `README.md` **and** the user does not want one created; otherwise **create** `README.md` with at least a title line plus **`Updated by Cursor.`** on the last line.

## 3. Discovery

0. **MCP scope:** GitHub MCP is **not** started by this playbook. Cursor only loads it from **`.cursor/mcp.json`** when the **workspace root** is the **orgwave-playbooks** repo folder. If the user opened a parent directory, point them to **`orgwave/required-mcp.md`** (*GitHub MCP missing in Cursor*).
1. **Listing — GitHub MCP only (when session has GitHub MCP):** Use **`search_repositories`** only — do **not** use **`gh api user/repos`**, **`gh repo list`**, or raw REST **for discovery** when GitHub MCP tools are available. Paginate (e.g. `user:<login>` for “my repos”, or `org:<org>`). **Do not** use MCP **`get_file_contents`**, **`create_branch`**, **`create_or_update_file`**, or **`push_files`** in this playbook.
2. **Listing — fallback when GitHub MCP is missing or fails:** Use **`gh api user/repos --paginate`** (filter `.permissions.push == true`, not archived) or **REST + `GITHUB_TOKEN`**. If **`gh` is not on PATH**, try **`/opt/homebrew/bin/gh`** / **`/usr/local/bin/gh`**, or **`brew install gh`** on macOS when Homebrew exists.
3. Print a **numbered** table: `#`, `full_name`, default branch (from search/API field when present), `html_url`. If the list came from **`search_repositories`**, add a column or footnote: **push not verified per row (MCP search)**.
4. **Stop** until the user selects repos (numbers, `owner/repo` list, or “all in table”).

## 4. Execution

Use **`gh`** and **git** for all repo file and branch work — **not** GitHub MCP file/branch/push tools.

Per **selected** repo (clone into workspace or temp path; respect user preference):

1. **Default branch:** Resolve with **`gh repo view <owner>/<repo> --json defaultBranchRef`** or **`gh api repos/<owner>/<repo> --jq .default_branch`**. If clone/checkout or PR **base** fails with **404**, retry using branch **`master`**, then **`main`**.
2. **Branch name:** **`techtask/readme-cursor-smoke-test`** from the resolved default (same ref for local **base** checkout and PR **`base`**).
3. Clone (if needed), create branch from default, edit **`README.md`** locally:
   - If it exists: ensure file ends with a newline, then append exactly: **`Updated by Cursor.`** on a new final line (no duplicate if that exact line already exists as the last line — skip or warn).
   - If it does not exist: create **`README.md`** with a one-line title (e.g. `# <repo name>`) and then **`Updated by Cursor.`** on the last line.
4. Commit: **`chore: append OrgWave smoke-test line to README`**
5. **`git push`** the branch (use **`gh auth`**-backed remote or HTTPS with token as appropriate).

## 5. PR

- **Open the PR with GitHub MCP only** when session tools exist: **`create_pull_request`** (`owner`, `repo`, `title`, `body`, `head`, `base`). If MCP fails after one retry, fall back to **`gh pr create`**.
- **Title:** `readme-cursor-smoke-test: README smoke test (OrgWave)`
- **Body:** Short explanation; link this **orgwave-playbooks** repo and playbook id **`readme-cursor-smoke-test`**; **do not merge** without owner review.

## 6. Checklist

- [ ] Discovery used **`search_repositories`** (MCP) when GitHub MCP was available; no duplicate listing via **`gh api`** in that case
- [ ] File/branch/push used **`gh`**/**git** only (no MCP file/branch/push tools)
- [ ] PR opened with **`create_pull_request`** (MCP) when available, else **`gh pr create`**
- [ ] User explicitly selected targets
- [ ] One PR per repo; agent did **not** merge

## Automation notes

- **Catalog / Run in Cursor:** `orgwave/catalog.yaml` — regenerate UI with `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`.
- **MCP / `.zshrc`:** [mcp-servers/README.md](../../mcp-servers/README.md), [orgwave/required-mcp.md](../../orgwave/required-mcp.md).
