---
name: orgwave-readme-cursor-smoke-test
description: Test playbook — prefer GitHub MCP for listing/PR when tools exist; gh/git for clone, branch, README, push; fall back to gh when MCP is absent; hard-stop only if github is undefined in mcp.json or no PAT.
---

# README Cursor smoke test

## Prerequisites

- **MCP servers required:** **`github`** — prefer **`search_repositories`** for discovery and **`create_pull_request`** for PRs **when** those tools exist in this session. **Do not stop** the run just because GitHub MCP tools did not attach to the agent; **continue** using **`gh`** / REST for listing and PRs per **Discovery** / **PR** below.
- **Hard stop — GitHub MCP not defined for this workspace:** If **`mcpServers.github`** is **absent** from **`.cursor/mcp.json`** at the workspace root, **stop** and tell the user to add **`mcp-servers/servers/github.json`**, run **`python3 orgwave/scripts/build-mcp-json.py`**, reload Cursor, enable **`github`** under **Tools & MCP**, then continue. If **`github`** is **in** **`mcp.json`** but disabled or tools do not attach, **do not stop** — note **`orgwave/required-mcp.md`** → *Enabling a disabled MCP server* if helpful and **continue** with **`gh`** for listing/PR when a PAT exists.
- **Hard stop — no PAT:** If there is **no** usable GitHub credential for **`gh`** or API (e.g. **`gh auth status`** shows not logged in / invalid token **and** repo **`.env`** / **`~/.cursor/github-mcp.env`** / launcher-merge path yields no valid token after a quick check), **stop** with **`mcp-servers/README.md`** + **`orgwave/required-mcp.md`** PAT guidance: **`export GITHUB_TOKEN=…`** or **`GITHUB_PERSONAL_ACCESS_TOKEN`** in **`~/.zshrc`** ( **`github-mcp-launch.mjs`** sources **`~/.zshrc`** when token keys are still empty), or **repo `.env`**, **`github-mcp.env`**, or **`gh auth login`**. **If a PAT works for `gh`**, keep going even when MCP returned **401/403** (use **`gh`** for discovery/PR for that run).

## 1. Intent

- **Change:** Append a single line to **`README.md`** at the repo root of each selected service: **`Updated by Cursor.`** (on its own line at the end of the file).
- **Done when:** Each chosen repo has an **open PR** with that README change. **Do not merge** unless the user asks.

## 2. Eligibility

- Repositories you intend to change should be ones the **same identity as GitHub MCP / `gh`** can **push** to (write). **`search_repositories`** does **not** return **`permissions.push`** per repo — state in the discovery table that rows are **MCP search candidates** (same token as MCP); exclude forks/archived if the search query supports it (`archived:false`, etc.).
- **Skip** if there is no `README.md` **and** the user does not want one created; otherwise **create** `README.md` with at least a title line plus **`Updated by Cursor.`** on the last line.

## 3. Discovery

0. **Config / credential (see Prerequisites):** Confirm **`mcpServers.github`** exists in **`.cursor/mcp.json`**. Confirm a **usable PAT** for **`gh`** (or REST) exists; if not, **hard stop** per Prerequisites — **do not** stop solely because GitHub MCP tools are missing from the agent session.
1. **Listing — prefer GitHub MCP:** When **`search_repositories`** is available, use it with pagination (e.g. `user:<login>`, `org:<org>`, `archived:false` / `fork:false` when useful). Retry **once** on transient MCP failure. For that discovery pass, **do not** also list via **`gh`** / REST. **Do not** use MCP **`get_file_contents`**, **`create_branch`**, **`create_or_update_file`**, or **`push_files`** in this playbook.
2. **Listing — fall back to `gh` (no stop):** If MCP tools are **not** in the session, **`search_repositories`** is unavailable, or it fails after retry **and** **`gh`** has a working token, use **`gh api user/repos --paginate`** / **`gh repo list`** or **REST + token** for discovery. If **`gh` is not on PATH**, try **`/opt/homebrew/bin/gh`** / **`/usr/local/bin/gh`**, or **`brew install gh`** on macOS when Homebrew exists.
3. Print a **numbered** table: `#`, `full_name`, default branch (from API/search when present), `html_url`. Footnote: if the list came from **`search_repositories`**, note **push not verified per row (MCP search)**; if from **`gh`** with push filter, say so; if mixed, say so briefly.
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

- **Prefer GitHub MCP:** When **`create_pull_request`** is available, use it (`owner`, `repo`, `title`, `body`, `head`, `base`). Retry **once** on transient failure.
- **Fall back to `gh` (no stop):** If the tool is unavailable or fails after retry **and** **`gh`** is authenticated, use **`gh pr create`** (or **`gh api`** for pulls). **Hard stop** only if there is **no** PAT for **`gh`** (same as Prerequisites) — not merely because MCP PR failed while **`gh`** could work.
- **Title:** `readme-cursor-smoke-test: README smoke test (OrgWave)`
- **Body:** Short explanation; link this **orgwave-playbooks** repo and playbook id **`readme-cursor-smoke-test`**; **do not merge** without owner review.

## 6. Checklist

- [ ] Discovery: **`search_repositories`** when MCP tools existed; otherwise **`gh`**/REST without unnecessary duplicate calls when MCP already succeeded
- [ ] File/branch/push used **`gh`**/**git** only (no MCP file/branch/push tools)
- [ ] PR: **`create_pull_request`** when MCP worked; otherwise **`gh pr create`** — no idle stop when PAT was available
- [ ] User explicitly selected targets
- [ ] One PR per repo; agent did **not** merge

## Automation notes

- **Catalog / Run in Cursor:** `orgwave/catalog.yaml` — regenerate UI with `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`.
- **MCP / `.zshrc`:** [mcp-servers/README.md](../../mcp-servers/README.md), [orgwave/required-mcp.md](../../orgwave/required-mcp.md).
