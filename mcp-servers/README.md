# MCP server definitions (OrgWave)

**Cursor only reads** [`.cursor/mcp.json`](../.cursor/mcp.json) at the workspace root ([Cursor MCP docs](https://cursor.com/docs/context/mcp)). This top-level folder is the **source of truth** for MCP: one JSON file per server; a script **merges** them into `.cursor/mcp.json`.

**Repo layout:** update **playbooks** under `playbooks/`; update **MCP servers** here — keep concerns separate.

## GitHub token (MCP vs `gh`)

The **github** server runs **`orgwave/scripts/github-mcp-launch.mjs`** (via **`node`** in **`.cursor/mcp.json`**), which sets **`GITHUB_PERSONAL_ACCESS_TOKEN`** for `@modelcontextprotocol/server-github` in this order:

1. Already set (e.g. repo-root **`.env`** via **`envFile`** — copy **`.env.example`**).
2. **User env file** (only if no token yet): **`~/.cursor/github-mcp.env`** or **`~/.config/orgwave/github-mcp.env`** — one line per variable, e.g. `GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...` or `GITHUB_TOKEN=...`. Use this when you open Cursor from the **Dock** or the GitHub **Run in Cursor** link (those paths do not load **`~/.zshrc`** into Cursor’s process).
3. **`~/.zshrc`** (macOS/Linux only, only if still no token): the launcher runs **`zsh`** and **sources** **`~/.zshrc`** non-interactively, then copies **`GITHUB_PERSONAL_ACCESS_TOKEN`**, **`GITHUB_TOKEN`**, and **`GH_TOKEN`** into the MCP process if they were set there. Keep **`export GITHUB_TOKEN=...`** (or PAT) in **`.zshrc`** so Dock-launched Cursor still gets a token. If **`.zshrc`** prints to stdout (e.g. `echo`), JSON parsing can fail — avoid noisy output on non-interactive source.
4. **`GITHUB_TOKEN`** passed from the Cursor process (`${env:GITHUB_TOKEN}` in `servers/github.json`).
5. **`GH_TOKEN`** (same idea as the GitHub CLI — often set when using `gh` in automation).
6. **`gh auth token`** if `gh` is installed and logged in. The launcher **prepends** **`/opt/homebrew/bin`** and **`/usr/local/bin`** to **`PATH`** so `gh` is found even when the MCP child’s **`PATH`** is minimal.

So **“`gh` works but GitHub MCP says Authentication Failed”** usually means none of the above were visible to the MCP child; fix with **`.env`**, **`~/.cursor/github-mcp.env`**, **`export`** in **`~/.zshrc`** (now picked up by the launcher), export **`GITHUB_TOKEN`** / **`GH_TOKEN`** before starting Cursor, or rely on **`gh auth login`** after this wrapper is in place.

### “Authentication Failed” vs “no permission”

| What you see | Typical meaning |
|--------------|-----------------|
| **Requires authentication** / **401** | GitHub did not get a **valid token** (missing, expired, or wrong). The API is not rejecting your PAT because it disallows writes in general — it often means **no credential** reached the server. |
| **Forbidden** / **403** / insufficient access | A token **was** accepted, but it **lacks scope** or **repo access** (e.g. read-only fine-grained token, or not a collaborator). Create a PAT with **repo** (classic) or **Contents**/**Pull requests** (fine-grained) for that repository. |

Reads on **public** repos can succeed **without** a token (rate-limited); **branches, file updates, and PRs** always need a valid token — so MCP can look fine for **`get_file_contents`** and then fail on **`create_branch`** / **`create_pull_request`** until a PAT is wired as above.

### Pinned install (recommended — faster connect)

Cold **`npx`** runs can take several seconds; some Cursor builds show **`Client closed`** / **empty offerings** while the client waits. **`github-mcp-launch.mjs`** prefers a pinned copy under **`orgwave/mcp-runtime/`** (spawns **`node`** on **`dist/index.js`** immediately). It avoids a shell wrapper calling **`gh`** on MCP’s stdin (that can cause **`Request timed out`** on initialize).

One-time (from repo root):

```bash
cd orgwave/mcp-runtime && npm ci
```

Commit **`package-lock.json`** is already in the repo; **`node_modules/`** is gitignored. If you skip this step, the script still falls back to **`npx`**.

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

**Windows:** **`node`** must be on `PATH` for **`github-mcp-launch.mjs`**. The **`npx`** fallback uses **`shell: true`** for **`npx.cmd`**. Prefer **`.env`** **`GITHUB_PERSONAL_ACCESS_TOKEN`** if **`gh`** is not available.

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
