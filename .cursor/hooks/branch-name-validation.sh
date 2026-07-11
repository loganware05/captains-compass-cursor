#!/usr/bin/env bash
# Require conventional branch names before git commit/push.
set -euo pipefail
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_common.sh"

compass_parse_input

if ! echo "$COMPASS_COMMAND" | grep -Eqi '(^|[[:space:]])git[[:space:]]+(commit|push)'; then
  compass_allow
fi

# Allow compound commands that create a valid branch first
if echo "$COMPASS_COMMAND" | grep -Eqi 'git[[:space:]]+checkout[[:space:]]+(-b|--branch)[[:space:]]+(feature|fix|chore|docs|agent|hotfix)/'; then
  compass_allow
fi

repo_dir="$(compass_repo_dir)"
branch="$(compass_branch "$repo_dir")"

if [[ -z "$branch" || "$branch" == "HEAD" ]]; then
  compass_allow
fi

# Protected bases are handled by protected-branch.sh; still reject odd names on commit/push
if echo "$branch" | grep -Eq '^(feature|fix|chore|docs|agent|hotfix)/[A-Za-z0-9._-]+'; then
  compass_allow
fi

compass_deny "Branch-name hook: branch '$branch' in $repo_dir should match feature|fix|chore|docs|agent|hotfix/<description>."
