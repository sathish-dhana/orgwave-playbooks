#!/usr/bin/env bash
# Called from .github/workflows/orgwave-run.yml with:
#   PLAYBOOK_ROOT, TARGET_REPO_DIR, REPO_SLUG, DRY_RUN, GH_TOKEN
set -euo pipefail

: "${TARGET_REPO_DIR:?TARGET_REPO_DIR not set}"
: "${REPO_SLUG:?REPO_SLUG not set}"

cd "${TARGET_REPO_DIR}"

: "${GH_TOKEN:-}"
if [ -n "${GH_TOKEN:-}" ]; then
  default_branch="$(gh api "repos/${REPO_SLUG}" --jq .default_branch)"
else
  default_branch="$(git rev-parse --abbrev-ref HEAD)"
fi

branch="${ORGWAVE_BRANCH:-techtask/example-migration-poc}"
git checkout -B "${branch}"

printf '%s\n' "Playbook: example-migration (POC) [via GitHub Actions run ${GITHUB_RUN_ID:-local}]" > ORGWAVE_PLAYBOOK.md

git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"

git add ORGWAVE_PLAYBOOK.md
if git diff --staged --quiet; then
  echo "No changes to commit for ${REPO_SLUG}"
  exit 0
fi

git commit -m "chore: add OrgWave playbook marker (POC)"

if [ "${DRY_RUN:-false}" = "true" ]; then
  echo "Dry run: skipping push and PR for ${REPO_SLUG}"
  exit 0
fi

: "${GH_TOKEN:?GH_TOKEN required when not dry_run}"

git push -u origin "${branch}"

body_file="$(mktemp)"
trap 'rm -f "${body_file}"' EXIT
cat > "${body_file}" <<EOF
Automated by [OrgWave playbooks](${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-org/orgwave-playbooks}) workflow \`orgwave-run.yml\`.

- **Playbook:** \`example-migration\`
- **Branch:** \`${branch}\`
- **Do not merge** without service owner review (POC marker only).
EOF

gh pr create \
  --repo "${REPO_SLUG}" \
  --title "example-migration: OrgWave POC marker" \
  --body-file "${body_file}" \
  --head "${branch}" \
  --base "${default_branch}"

echo "Opened PR for ${REPO_SLUG}"
