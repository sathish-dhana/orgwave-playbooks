# MCP server definitions (OrgWave)

**Cursor only reads** [`.cursor/mcp.json`](../.cursor/mcp.json) at the workspace root ([Cursor MCP docs](https://cursor.com/docs/context/mcp)). This top-level folder is the **source of truth** for MCP: one JSON file per server; a script **merges** them into `.cursor/mcp.json`.

**Repo layout:** update **playbooks** under `playbooks/`; update **MCP servers** here — keep concerns separate.

## GitHub token (MCP vs `gh`)

The **github** server runs **`orgwave/scripts/github-mcp-launch.sh`**, which sets **`GITHUB_PERSONAL_ACCESS_TOKEN`** for `@modelcontextprotocol/server-github` in this order:

1. Already set (e.g. repo-root **`.env`** via **`envFile`** — copy **`.env.example`**).
2. **`GITHUB_TOKEN`** passed from the Cursor process (`${env:GITHUB_TOKEN}` in `servers/github.json`).
3. **`GH_TOKEN`** (same idea as the GitHub CLI — often set when using `gh` in automation).
4. **`gh auth token`** if `gh` is installed and logged in (Homebrew paths are tried first).

So **“`gh` works but GitHub MCP says Authentication Failed”** usually means none of the above were visible to the MCP child; fix with **`.env`**, export **`GITHUB_TOKEN`** or **`GH_TOKEN`** before starting Cursor, or rely on **`gh auth login`** after this wrapper is in place.

### Recommended: `GITHUB_TOKEN` + `~/.zshrc`

1. Put the token in **`~/.zshrc`** (fix the path — it is **`.zshrc`**, not `.zhrc`):

   ```bash
   echo 'export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Start Cursor from the same terminal** so the GUI inherits `GITHUB_TOKEN`:

   ```bash
   open -a Cursor /path/to/orgwave-playbooks
   ```

   If you only click the Cursor icon in the Dock, macOS often **does not** load `~/.zshrc` into that process — use **`.env`** or ensure **`gh`** is logged in so the launch script can read a token.

**Windows:** the launch script is **bash** — use **Git Bash** / **WSL**, or rely on **`.env`** **`GITHUB_PERSONAL_ACCESS_TOKEN`** only (no `gh` fallback unless `gh` is on `PATH` in that environment).

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

## Enabling a server that is disabled in Cursor

A server can be **defined** in **`.cursor/mcp.json`** but **turned off** in the editor. In **Cursor Settings → Tools & MCP**, find the server by **`mcpServers.<id>`** (e.g. **`github`**) and **enable** it; reload the window if tools do not appear. Full steps and agent behaviour: **`orgwave/required-mcp.md`** → *Enabling a disabled MCP server*.

## See also

- **`orgwave/required-mcp.md`** — policy (non-blocking, fallbacks).
- **`orgwave/scripts/build-mcp-json.py`** — merge implementation.
