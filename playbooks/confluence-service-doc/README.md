<!-- orgwave-generated -->
# Confluence service stub

Playbook id: `confluence-service-doc`

[![Play — Run in Cursor](https://img.shields.io/badge/-Run_in_Cursor-22c55e?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI%2BPHBhdGggZmlsbD0iI2ZmZiIgZD0iTTggNXYxNGwxMS03eiIvPjwvc3ZnPg%3D%3D)](https://cursor.com/link/prompt?text=OrgWave%3A%20open%20orgwave-playbooks%20as%20workspace.%20Run%20orchestrator%20rule%20and%20playbook%20confluence-service-doc.%20Read%20orgwave%2Fcatalog.yaml%20playbooks%2Fconfluence-service-doc%2FSKILL.md%20and%20orgwave%2Frequired-mcp.md.%20Complete%20Prerequisites%20in%20playbooks%2Fconfluence-service-doc%2FSKILL.md%20first.%20For%20each%20MCP%20server%20id%20listed%20under%20MCP%20servers%20required%20confirm%20mcpServers%20that%20id%20exists%20in%20repo%20root%20dot%20cursor%20mcp%20dot%20json.%20If%20a%20required%20id%20is%20missing%20stop%20tell%20user%20add%20mcp-servers%2Fservers%20that%20id%20dot%20json%20per%20mcp-servers%20README%20run%20python3%20orgwave%2Fscripts%2Fbuild-mcp-json.py%20reload%20Cursor%20enable%20the%20server.%20If%20a%20required%20server%20is%20disabled%20tools%20missing%20in%20session%20or%20PAT%20auth%20fails%20after%20one%20retry%20stop%20with%20orgwave%2Frequired-mcp.md%20gate%20and%20mcp-servers%20README%20then%20user%20fixes%20and%20Reload%20Window.%20If%20all%20prerequisites%20pass%20continue%20using%20only%20those%20MCP%20servers%20for%20steps%20the%20playbook%20assigns%20to%20them%20no%20gh%20git%20or%20ad%20hoc%20GitHub%20REST.%20GitHub%20token%20for%20MCP%20child%20github-mcp-launch%20merges%20envFile%20dot%20env%20github-mcp%20dot%20env%20and%20zshrc%20when%20keys%20empty%20see%20mcp-servers%20README.%20search_repositories%20does%20not%20include%20permissions%20push%20per%20row%20say%20so%20in%20the%20table.%20Resolve%20default%20branch%20from%20MCP%20metadata%20if%20Not%20Found%20on%20file%20branch%20or%20PR%20base%20try%20master%20then%20main.%20Discover%20repos%20numbered%20table%20stop%20for%20my%20selection%20one%20PR%20per%20repo%20do%20not%20merge.)

Click the **play** button to open Cursor with this playbook's prompt prefilled - you still confirm before the agent runs.

If Cursor shows **invalid text for prompt**, paste this into Agent chat instead:

```text
OrgWave: open orgwave-playbooks as workspace. Run orchestrator rule and playbook confluence-service-doc. Read orgwave/catalog.yaml playbooks/confluence-service-doc/SKILL.md and orgwave/required-mcp.md. Complete Prerequisites in playbooks/confluence-service-doc/SKILL.md first. For each MCP server id listed under MCP servers required confirm mcpServers that id exists in repo root dot cursor mcp dot json. If a required id is missing stop tell user add mcp-servers/servers that id dot json per mcp-servers README run python3 orgwave/scripts/build-mcp-json.py reload Cursor enable the server. If a required server is disabled tools missing in session or PAT auth fails after one retry stop with orgwave/required-mcp.md gate and mcp-servers README then user fixes and Reload Window. If all prerequisites pass continue using only those MCP servers for steps the playbook assigns to them no gh git or ad hoc GitHub REST. GitHub token for MCP child github-mcp-launch merges envFile dot env github-mcp dot env and zshrc when keys empty see mcp-servers README. search_repositories does not include permissions push per row say so in the table. Resolve default branch from MCP metadata if Not Found on file branch or PR base try master then main. Discover repos numbered table stop for my selection one PR per repo do not merge.
```

- Agent instructions: **[SKILL.md](SKILL.md)**
- All playbooks: **[orgwave/docs/run-in-cursor.md](../../orgwave/docs/run-in-cursor.md)**

---

*Auto-generated from `orgwave/catalog.yaml` — do not edit the block above by hand. Regenerate with* `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`*.*

## Terminal: Confluence email and token (repo `.env`)

**`CONFLUENCE_BASE_URL`** is pinned in **`mcp-servers/servers/confluence.json`** (`https://confluence.myntracorp.com/`). From the **repo root**, append **email** and **token** only (replace placeholders):

```bash
cd /path/to/orgwave-playbooks
umask 077
cat >> .env << 'EOF'
CONFLUENCE_USER_EMAIL=you@myntracorp.com
CONFLUENCE_API_TOKEN=your_confluence_personal_access_token
EOF
```

Then **`python3 orgwave/scripts/build-mcp-json.py`** if you changed server JSON, **Developer: Reload Window**, and enable **`confluence`** under Tools & MCP. Details: **[mcp-servers/README.md](../../mcp-servers/README.md)**.
