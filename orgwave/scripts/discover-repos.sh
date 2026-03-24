#!/usr/bin/env bash
# List org repos via gh (GitHub API — same data GitHub MCP uses), apply optional playbooks/<id>/discovery.json filters.
# Env: ORG, PLAYBOOK_ID, optional GITHUB_WORKSPACE / repo root, OUT_JSON (default discovery-output.json)
set -euo pipefail

ORG="${ORG:?set ORG to GitHub org or user login}"
PLAYBOOK_ID="${PLAYBOOK_ID:?set PLAYBOOK_ID}"
ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
OUT_JSON="${OUT_JSON:-discovery-output.json}"
FILTER_FILE="${ROOT}/playbooks/${PLAYBOOK_ID}/discovery.json"

if [[ ! -d "${ROOT}/playbooks/${PLAYBOOK_ID}" ]]; then
  echo "Unknown playbook: ${PLAYBOOK_ID} (no playbooks/${PLAYBOOK_ID})" >&2
  exit 1
fi

export GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"

ALL_JSON="$(gh repo list "${ORG}" --limit 8000 --json nameWithOwner,isArchived,defaultBranchRef,url,repositoryTopics)"

# Normalize (handles repositoryTopics as array or { nodes: [{name}] })
NORMALIZED="$(echo "${ALL_JSON}" | jq '
  map({
    full_name: .nameWithOwner,
    archived: .isArchived,
    default_branch: (.defaultBranchRef.name // "main"),
    html_url: .url,
    topics: (
      (.repositoryTopics // null) as $t
      | if $t == null then []
        elif ($t | type) == "array" then [ $t[] | (.name // .) ]
        elif ($t | type) == "object" and ($t.nodes != null) then [ $t.nodes[] | .name ]
        else []
        end
    )
  })
')"

if [[ -f "${FILTER_FILE}" ]]; then
  echo "${NORMALIZED}" | jq --rawfile cfg "${FILTER_FILE}" '
    ($cfg | fromjson) as $c
    | map(select(.archived == ($c.archived // false)))
    | map(select(
        ($c.include_name_regex == null or $c.include_name_regex == "")
        or (.full_name | test($c.include_name_regex))
      ))
    | map(select(
        ($c.exclude_name_regex == null or $c.exclude_name_regex == "")
        or (.full_name | test($c.exclude_name_regex) | not)
      ))
    | map(select(
        ($c.require_topics_any == null)
        or (($c.require_topics_any | length) == 0)
        or (any($c.require_topics_any[] as $req | (.topics | index($req) != null)))
      ))
  ' > "${OUT_JSON}"
else
  echo "${NORMALIZED}" | jq 'map(select(.archived == false))' > "${OUT_JSON}"
fi

COUNT="$(jq 'length' "${OUT_JSON}")"
echo "Wrote ${COUNT} repos to ${OUT_JSON}" >&2
