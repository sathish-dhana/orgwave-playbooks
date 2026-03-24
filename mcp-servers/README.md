# MCP server definitions (OrgWave)

**Cursor only reads** [`.cursor/mcp.json`](../.cursor/mcp.json) at the workspace root ([Cursor MCP docs](https://cursor.com/docs/context/mcp)). This top-level folder is the **source of truth** for MCP: one JSON file per server; a script **merges** them into `.cursor/mcp.json`.

**Repo layout:** update **playbooks** under `playbooks/`; update **MCP servers** here — keep concerns separate.

## GitHub token (`GITHUB_TOKEN` + `~/.zshrc`)

The **github** server uses **`${env:GITHUB_TOKEN}`** (see `servers/github.json`). That value is read from the **environment Cursor had when it started**, not from a URL when you click “Run in Cursor” on GitHub.

1. Put the token in **`~/.zshrc`** (fix the path — it is **`.zshrc`**, not `.zhrc`):

   ```bash
   echo 'export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Start Cursor from the same terminal** so the GUI inherits `GITHUB_TOKEN`:

   ```bash
   open -a Cursor /path/to/orgwave-playbooks
   ```

   If you only click the Cursor icon in the Dock, macOS often **does not** load `~/.zshrc` into that process — MCP will not see the token.

**Optional:** repo-root **`.env`** with **`GITHUB_PERSONAL_ACCESS_TOKEN`** (copy **`.env.example`**). `github.json` sets **`envFile`** to **`${workspaceFolder}/.env`** as a fallback for tools that read the file directly.

## Add a server

1. Create **`servers/<id>.json`** where **`<id>`** is the MCP server key Cursor uses (must match `server` in `~/.cursor/permissions.json` patterns like `<id>:*`).
2. File content = **one** server object in Cursor’s format (same fields as inside `mcpServers.<id>`).
3. Optional top-level **`_orgwave`**: metadata for humans and the agent (not written to `mcp.json`).

```bash
# From repository root — regenerates .cursor/mcp.json
python3 orgwave/scripts/build-mcp-json.py
```

Commit **both** `mcp-servers/servers/*.json` and the updated **`.cursor/mcp.json`**.

### Filename rules

| Rule | |
|------|--|
| **Name** | `servers/<id>.json` — use only `[a-z0-9-]+` for `<id>` (e.g. `github`, `linear`). |
| **Skip** | Files whose name starts with **`_`** are ignored (templates / notes only). |
| **Secrets** | Never commit tokens. Use **`${env:VAR_NAME}`** in `env` / `headers` per [config interpolation](https://cursor.com/docs/context/mcp). |

### Standard shape (stdio — most common)

```json
{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "some-mcp-package"],
  "env": {
    "API_TOKEN": "${env:MY_ORG_API_TOKEN}"
  },
  "_orgwave": {
    "title": "Human name",
    "purpose": "What OrgWave uses it for (discovery, PRs, …).",
    "env": ["MY_ORG_API_TOKEN"],
    "permissionsAllowlistHint": "myserver:*"
  }
}
```

### Remote server (HTTP / SSE)

```json
{
  "url": "https://api.example.com/mcp",
  "headers": {
    "Authorization": "Bearer ${env:EXAMPLE_TOKEN}"
  },
  "_orgwave": {
    "title": "Example remote",
    "purpose": "…",
    "env": ["EXAMPLE_TOKEN"]
  }
}
```

Follow [Cursor MCP — Remote Server](https://cursor.com/docs/context/mcp) for OAuth and other fields.

### `_orgwave` fields (optional, all optional)

| Field | Meaning |
|-------|---------|
| `title` | Display name in docs. |
| `purpose` | When the agent should prefer this server. |
| `env` | List of env var names users must set for the token/secret. |
| `permissionsAllowlistHint` | Suggested `mcpAllowlist` entry for `~/.cursor/permissions.json`. |

## Behaviour with prompts

- If **`_orgwave.env`** vars are available to Cursor’s MCP process, that server **can** auto-start and tools appear to the agent.
- If not, OrgWave **does not block** — fall back to `gh`, other MCP servers, or `discovery-output.json` per **`orgwave/required-mcp.md`** and the playbook **`SKILL.md`**.

## See also

- **`orgwave/required-mcp.md`** — policy (non-blocking, fallbacks).
- **`orgwave/scripts/build-mcp-json.py`** — merge implementation.
