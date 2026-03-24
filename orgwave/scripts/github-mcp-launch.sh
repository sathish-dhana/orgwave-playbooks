#!/usr/bin/env bash
# Launch @modelcontextprotocol/server-github with a PAT even when only gh CLI is logged in.
# Cursor merges envFile + mcp env before exec; this script fills GITHUB_PERSONAL_ACCESS_TOKEN if missing.
set -euo pipefail

if [[ -z "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    export GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_TOKEN"
  elif [[ -n "${GH_TOKEN:-}" ]]; then
    export GITHUB_PERSONAL_ACCESS_TOKEN="$GH_TOKEN"
  else
    PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
    if command -v gh >/dev/null 2>&1; then
      if t="$(gh auth token 2>/dev/null)" && [[ -n "$t" ]]; then
        export GITHUB_PERSONAL_ACCESS_TOKEN="$t"
      fi
    fi
  fi
fi

exec npx -y @modelcontextprotocol/server-github "$@"
