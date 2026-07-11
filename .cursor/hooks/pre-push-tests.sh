#!/usr/bin/env bash
# Before git push, run npm test when available. Skip with COMPASS_SKIP_TESTS=1.
set -euo pipefail
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_common.sh"

compass_parse_input

if ! echo "$COMPASS_COMMAND" | grep -Eqi '(^|[[:space:]])git[[:space:]]+push'; then
  compass_allow
fi

# Tag-only pushes should not require app tests
if echo "$COMPASS_COMMAND" | grep -Eqi 'git[[:space:]]+push[^;]*[[:space:]]v?[0-9]+\.[0-9]+'; then
  compass_allow
fi
if echo "$COMPASS_COMMAND" | grep -Eqi 'refs/tags/|origin[[:space:]]+v[0-9]'; then
  compass_allow
fi

if [[ "${COMPASS_SKIP_TESTS:-}" == "1" ]]; then
  compass_allow
fi

repo_dir="$(compass_repo_dir)"
if [[ ! -f "$repo_dir/package.json" ]]; then
  compass_allow
fi

if ! python3 -c 'import json,sys; s=json.load(open(sys.argv[1])).get("scripts") or {}; sys.exit(0 if "test" in s else 1)' "$repo_dir/package.json"; then
  compass_allow
fi

if (cd "$repo_dir" && npm test --silent); then
  compass_allow
fi

compass_deny "Pre-push tests hook: npm test failed in $repo_dir. Fix tests or set COMPASS_SKIP_TESTS=1."
