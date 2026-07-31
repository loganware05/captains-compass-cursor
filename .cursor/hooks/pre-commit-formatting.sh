#!/usr/bin/env bash
# Before git commit, run npm format or lint when available. Skip with COMPASS_SKIP_FORMAT=1.
set -euo pipefail
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_common.sh"

compass_parse_input

if ! echo "$COMPASS_COMMAND" | grep -Eqi '(^|[[:space:]])git[[:space:]]+commit'; then
  compass_allow
fi

if compass_soft_skip FORMAT; then
  compass_allow
fi

repo_dir="$(compass_repo_dir)"
if [[ ! -f "$repo_dir/package.json" ]]; then
  compass_allow
fi

has_script() {
  local name="$1"
  python3 -c 'import json,sys; s=json.load(open(sys.argv[1])).get("scripts") or {}; sys.exit(0 if sys.argv[2] in s else 1)' "$repo_dir/package.json" "$name"
}

if has_script format; then
  if ! (cd "$repo_dir" && npm run format --silent); then
    compass_deny "Pre-commit formatting hook: npm run format failed in $repo_dir. Fix formatting or set COMPASS_SKIP_FORMAT=1."
  fi
elif has_script lint; then
  if ! (cd "$repo_dir" && npm run lint --silent); then
    compass_deny "Pre-commit formatting hook: npm run lint failed in $repo_dir. Fix lint issues or set COMPASS_SKIP_FORMAT=1."
  fi
fi

compass_allow
