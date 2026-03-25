---
name: orgwave-example-migration
description: Sample OrgWave playbook — discover via GitHub MCP, select repos, add a POC marker file, open PRs via MCP only.
---

# Example migration (POC)

## Prerequisites

- **MCP servers required:** **`github`**. Use **only** GitHub MCP tools for GitHub operations (discovery, branches, files, PRs).
- **Hard stop — definition:** If **`mcpServers.github`** is **absent** from **`.cursor/mcp.json`**, **stop** and instruct: **`mcp-servers/servers/github.json`**, **`python3 orgwave/scripts/build-mcp-json.py`**, reload, enable **`github`**.
- **Hard stop — not enabled or tools missing:** If **`github`** is off or tools do not attach, **stop** per **`orgwave/required-mcp.md`**.
- **Hard stop — auth:** **401** / **403** after one retry → **stop** with **`mcp-servers/README.md`** and **`orgwave/required-mcp.md`** PAT guidance.

When prerequisites pass, **continue**.

## 1. Intent

- **Change:** Add a small marker file to show the OrgWave flow.
- **Done when:** Each chosen repo has an open PR with that change.

## 2. Eligibility

- Same GitHub org / scope the user names; not archived.
- Exclude names containing `archived-` or `deprecated-` if you keep that policy.

## 3. Discovery

1. List repos with GitHub MCP **`search_repositories`** (or other GitHub MCP listing tools the server provides), scoped to the org/user the user names. Retry once on transient failure; then **stop** if still failing.
2. Numbered table: `#`, name, default branch when present, `html_url`. Note **push not verified per row** if using search. **Stop** for selection.

## 4. Execution

Per selected repo — **GitHub MCP only**:

- Resolve **default branch** from MCP metadata; on **404**, try **`master`** then **`main`**.
- Branch: **`techtask/example-migration-poc`**
- Add or update **`ORGWAVE_PLAYBOOK.md`** at repo root: `Playbook: example-migration (POC)` using MCP branch/file/push tools.
- Commit message when supported: `chore: add OrgWave playbook marker (POC)`; push via MCP; open PR via MCP.

## 5. PR

- Use **`create_pull_request`** (retry once; then **stop** if needed).
- **Title:** `example-migration: OrgWave POC marker`
- **Body:** Link this playbooks repo; POC only; **do not merge** without review.

## 6. Checklist

- [ ] Prerequisites passed or run **stopped** with gate
- [ ] User selected repos explicitly
- [ ] GitHub steps used **only** MCP tools
- [ ] One PR per service
- [ ] No merge by agent

## Automation notes

- **Run in Cursor:** `orgwave/catalog.yaml`; regenerate with `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`.
- **MCP:** [mcp-servers/servers/](../../mcp-servers/servers/) — [mcp-servers/README.md](../../mcp-servers/README.md); **`python3 orgwave/scripts/build-mcp-json.py`**.
