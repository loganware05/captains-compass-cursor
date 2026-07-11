#!/usr/bin/env bash
# Before gh pr create, require an approved/complete plan and evidence files.
# Skip with COMPASS_SKIP_PR_EVIDENCE=1.
set -euo pipefail
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$HOOK_DIR/_common.sh"

compass_parse_input

if ! echo "$COMPASS_COMMAND" | grep -Eqi '(^|[[:space:]])gh[[:space:]]+pr[[:space:]]+create'; then
  compass_allow
fi

if [[ "${COMPASS_SKIP_PR_EVIDENCE:-}" == "1" ]]; then
  compass_allow
fi

repo_dir="$(compass_repo_dir)"

if [[ ! -f "$repo_dir/IMPLEMENTATION_PLAN.md" ]]; then
  compass_deny "PR evidence hook: IMPLEMENTATION_PLAN.md missing in $repo_dir. Complete the Compass workflow before opening a PR."
fi

status_line="$(grep -E '^- Status:' "$repo_dir/IMPLEMENTATION_PLAN.md" | head -1 || true)"
if ! echo "$status_line" | grep -Eqi 'APPROVED|IN PROGRESS|VALIDATING|COMPLETE'; then
  compass_deny "PR evidence hook: plan status must be APPROVED or later before gh pr create (found: ${status_line:-none})."
fi

if [[ ! -d "$repo_dir/.agent/evidence" ]]; then
  compass_deny "PR evidence hook: .agent/evidence/ missing in $repo_dir. Record validation evidence before opening a PR."
fi

if [[ -z "$(find "$repo_dir/.agent/evidence" -type f 2>/dev/null | head -1)" ]]; then
  compass_deny "PR evidence hook: .agent/evidence/ has no files in $repo_dir. Add test/screenshot/security evidence before gh pr create."
fi

compass_allow
