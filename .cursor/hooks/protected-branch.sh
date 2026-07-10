#!/usr/bin/env bash
# Block commits and pushes directly on protected base branches.
set -euo pipefail

input="$(cat)"
command="$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("command") or "")' <<<"$input")"

# Only gate mutating git commands
if ! echo "$command" | grep -Eqi '(^|[[:space:]])git[[:space:]]+(commit|push|merge|rebase)'; then
  echo '{"permission":"allow"}'
  exit 0
fi

branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
case "$branch" in
  main|master|develop|release|production)
    msg="Protected-branch hook: refusing git mutation on protected branch '$branch'. Use a feature/fix branch."
    python3 -c 'import json,sys; print(json.dumps({"permission":"deny","user_message":sys.argv[1],"agent_message":sys.argv[1]}))' "$msg"
    exit 0
    ;;
esac

echo '{"permission":"allow"}'
exit 0
