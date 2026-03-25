# MCP server definitions (OrgWave)

**Cursor only reads** [`.cursor/mcp.json`](../.cursor/mcp.json) at the workspace root ([Cursor MCP docs](https://cursor.com/docs/context/mcp)). This top-level folder is the **source of truth** for MCP: one JSON file per server; a script **merges** them into `.cursor/mcp.json`.

**Repo layout:** update **playbooks** under `playbooks/`; update **MCP servers** here — keep concerns separate.

## GitHub token (MCP vs `gh`)

The **github** server runs **`orgwave/scripts/github-mcp-launch.mjs`** (via **`node`** in **`.cursor/mcp.json`**), which sets **`GITHUB_PERSONAL_ACCESS_TOKEN`** for `@modelcontextprotocol/server-github`.

### Merge phase (before choosing a PAT)

Cursor passes **`envFile`** (repo **`.env`**) into the MCP process. **`servers/github.json`** intentionally has **no** **`env`** block with **`${env:GITHUB_TOKEN}`** so Cursor does not inject **empty** token vars that would block **`github-mcp.env`** / **`.zshrc`** merge. The launcher then:

1. **Prepends** **`/opt/homebrew/bin`** and **`/usr/local/bin`** to **`PATH`** so **`gh`** is found.
2. **Reads** **`~/.cursor/github-mcp.env`** and **`~/.config/orgwave/github-mcp.env`** and sets **`GITHUB_PERSONAL_ACCESS_TOKEN`**, **`GITHUB_TOKEN`**, **`GH_TOKEN`**, and **`ORGWAVE_MCP_PREFER_ENV_TOKEN`** only for keys that are **still empty**.
3. **Sources** **`~/.zshrc`** (macOS/Linux, non-interactive) and copies the same three token vars only where **still empty**. Avoid noisy **`echo`** on non-interactive source (can break the probe). **`export GITHUB_TOKEN=...`** in **`.zshrc`** is the usual fix when Cursor was started from the Dock and has no token in its own environment.

### Which credential wins

1. **`GITHUB_PERSONAL_ACCESS_TOKEN`** if non-empty after the merge phase (repo **`.env`** is the usual place — copy **`.env.example`**). This always wins.
2. **Default:** **`gh auth token`** next (same identity as **`gh`** in the terminal), then **`GITHUB_TOKEN`**, then **`GH_TOKEN`**. That fixes the common case where **`gh`** works but MCP saw a **stale or empty** token from Cursor’s environment and private repos returned **404** / **Not Found**.
3. **Override:** set **`ORGWAVE_MCP_PREFER_ENV_TOKEN=1`** in **`.env`** or **`github-mcp.env`** to use **`GITHUB_TOKEN`** / **`GH_TOKEN`** **before** **`gh`** (e.g. automation PAT while **`gh`** is another user).

So **“`gh` works but GitHub MCP fails”** is often **wrong token order** or **no token in the MCP child** — use **`.env`** **`GITHUB_PERSONAL_ACCESS_TOKEN`**, **`github-mcp.env`**, rely on the default **`gh`-first** behavior after reload, or set **`ORGWAVE_MCP_PREFER_ENV_TOKEN`** when you need env-first.

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

## Confluence (`confluence` server)

The **`confluence`** entry uses a **pinned** copy of [**`@answerai/confluence-mcp`**](https://www.npmjs.com/package/@answerai/confluence-mcp) under **`orgwave/mcp-confluence-runtime/`** (same idea as GitHub under **`orgwave/mcp-runtime/`**).

**One-time** (from repo root):

```bash
cd orgwave/mcp-confluence-runtime && npm ci
```

**Secrets** (repo **`.env`**, loaded via **`envFile`** in **`servers/confluence.json`** — never commit values). In **this** repo, **`CONFLUENCE_BASE_URL`** is **pinned** in **`servers/confluence.json`** (`https://confluence.myntracorp.com/`); you normally set only email and token in **`.env`**.

| Variable | Role |
|----------|------|
| **`CONFLUENCE_BASE_URL`** | In **`servers/confluence.json`** → **`env`** for OrgWave default. Else Cloud: `https://<site>.atlassian.net/wiki`; Server/DC: your site base. |
| **`CONFLUENCE_USER_EMAIL`** | Account email for the Confluence API / PAT. |
| **`CONFLUENCE_API_TOKEN`** | Confluence personal access token or (Cloud) [Atlassian API token](https://id.atlassian.com/manage-profile/security/api-tokens). |

Copy **[`.env.example`](../.env.example)** placeholders, reload Cursor, enable **`confluence`** under **Tools & MCP**. Terminal snippets: **[`playbooks/confluence-service-doc/README.md`](../playbooks/confluence-service-doc/README.md)**.

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
- If a playbook **requires** a server and it is missing, disabled, or unauthenticated, the agent **stops** with **`orgwave/required-mcp.md`** — **no** **`gh`** / REST substitute for that server’s steps.

## Enabling a server that is disabled in Cursor

A server can be **defined** in **`.cursor/mcp.json`** but **turned off** in the editor. In **Cursor Settings → Tools & MCP**, find the server by **`mcpServers.<id>`** (e.g. **`github`**) and **enable** it; reload the window if tools do not appear. Full steps and agent behaviour: **`orgwave/required-mcp.md`** → *Enabling a disabled MCP server*.

## See also

- **`orgwave/required-mcp.md`** — policy (MCP gate, reload, PAT).
- **`orgwave/scripts/build-mcp-json.py`** — merge implementation.
