---
name: orgwave-readme-cursor-smoke-test
description: Test playbook — GitHub MCP only for discovery, file/branch, push, and PRs; stop if prerequisites fail.
---

# README Cursor smoke test

## Prerequisites

- **MCP servers required:** **`github`**. All GitHub steps use **only** GitHub MCP tools (no shell **`git`**, **`gh`**, or ad-hoc REST from the agent).
- **Hard stop — definition:** If **`mcpServers.github`** is **absent** from **`.cursor/mcp.json`** at the workspace root, **stop**. Tell the user to add **`mcp-servers/servers/github.json`**, run **`python3 orgwave/scripts/build-mcp-json.py`**, reload Cursor, enable **`github`** under **Tools & MCP**, then continue in a new message.
- **Hard stop — not enabled or tools missing:** If **`github`** is listed but **disabled**, or GitHub MCP tools **do not appear in this agent session**, **stop** with **`orgwave/required-mcp.md`** → *GitHub MCP gate* and *Enabling a disabled MCP server* (reload window, new message). **Do not** substitute CLI or REST.
- **Hard stop — no PAT / auth:** If GitHub MCP returns **401**, **403**, or **Requires authentication** after **one** retry on the same tool, **stop** with **`mcp-servers/README.md`** and **`orgwave/required-mcp.md`** PAT guidance (repo **`.env`** **`GITHUB_PERSONAL_ACCESS_TOKEN`**, **`~/.cursor/github-mcp.env`**, **`~/.zshrc`** exports, launcher merge order — see README).

When every prerequisite above passes, **continue** the playbook.

## 1. Intent

- **Change:** Append a single line to **`README.md`** at the repo root of each selected service: **`Updated by Cursor.`** (on its own line at the end of the file).
- **Done when:** Each chosen repo has an **open PR** with that README change. **Do not merge** unless the user asks.

## 2. Eligibility

- Repositories the same GitHub identity as MCP can **push** to. **`search_repositories`** does **not** return **`permissions.push`** per row — state in the discovery table that rows are **MCP search candidates**; exclude forks/archived when the query supports it (`archived:false`, etc.).
- **Skip** if there is no `README.md` **and** the user does not want one created; otherwise **create** `README.md` with at least a title line plus **`Updated by Cursor.`** on the last line.

## 3. Discovery

1. Use GitHub MCP **`search_repositories`** with pagination (e.g. `user:<login>`, `org:<org>`, `archived:false` / `fork:false` when useful). Retry **once** on transient failure; if it still fails, **stop** (auth or gate per Prerequisites).
2. Print a **numbered** table: `#`, `full_name`, default branch when the MCP response includes it, `html_url`. Footnote: **push not verified per row (MCP search)**.
3. **Stop** until the user selects repos (numbers, `owner/repo` list, or “all in table”).

## 4. Execution (GitHub MCP only)

Per **selected** repo:

1. **Default branch:** Resolve from GitHub MCP repository metadata or discovery payload. If a later MCP call returns **404** / **Not Found** for the assumed default ref, retry **`base`** / ref as **`master`**, then **`main`**.
2. **Branch name:** **`techtask/readme-cursor-smoke-test`** from the resolved default (same ref for PR **`base`**).
3. Use GitHub MCP to create the branch and apply the README change (e.g. **`get_file_contents`**, **`create_branch`**, **`create_or_update_file`**, **`push_files`** — use whichever tools the server exposes for this flow). Do **not** use MCP **`get_file_contents`** only to bypass push when **`push_files`** is the supported path; follow the server’s normal commit model.
   - If **`README.md`** exists: ensure content ends with a newline, then append exactly **`Updated by Cursor.`** on a new final line (no duplicate if that exact line is already the last line — skip or warn).
   - If it does not exist: create **`README.md`** with a one-line title (e.g. `# <repo name>`) and **`Updated by Cursor.`** on the last line.
4. Commit message (when the MCP tool accepts it): **`chore: append OrgWave smoke-test line to README`**

## 5. PR

- Open the PR with GitHub MCP **`create_pull_request`** (`owner`, `repo`, `title`, `body`, `head`, `base`). Retry **once** on transient failure; if it still fails, **stop** with the gate / PAT guidance.
- **Title:** `readme-cursor-smoke-test: README smoke test (OrgWave)`
- **Body:** Short explanation; link this **orgwave-playbooks** repo and playbook id **`readme-cursor-smoke-test`**; **do not merge** without owner review.

## 6. Checklist

- [ ] Prerequisites passed or run **stopped** with gate message
- [ ] Discovery used **`search_repositories`** only
- [ ] Branch, README change, and push used **only** GitHub MCP file/branch/push tools
- [ ] PR opened with **`create_pull_request`** only
- [ ] User explicitly selected targets
- [ ] One PR per repo; agent did **not** merge

## Automation notes

- **Catalog / Run in Cursor:** `orgwave/catalog.yaml` — regenerate UI with `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`.
- **MCP / tokens:** [mcp-servers/README.md](../../mcp-servers/README.md), [orgwave/required-mcp.md](../../orgwave/required-mcp.md).
