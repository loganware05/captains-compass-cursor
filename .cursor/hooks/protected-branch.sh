#!/usr/bin/env bash
# Block commits and pushes directly on protected base branches.
# Resolves the target git repo from hook cwd or a leading `cd` in the command.
set -euo pipefail

input="$(cat)"

COMMAND="$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("command") or "")')"
HOOK_CWD="$(printf '%s' "$input" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("cwd") or d.get("working_directory") or d.get("workingDirectory") or "")')"
CD_PATH="$(printf '%s' "$input" | python3 -c '
import json,sys,re
command=json.load(sys.stdin).get("command") or ""
m=re.search(r"(?:^|[;&\n])\s*cd\s+(\"([^\"]+)\"|'\''([^'\'']+)'\''|(\S+))\s*(?:&&|;|\n)", command)
if not m:
    print("")
else:
    print(m.group(2) or m.group(3) or m.group(4) or "")
')"

allow() { echo '{"permission":"allow"}'; exit 0; }
deny() {
  python3 -c 'import json,sys; print(json.dumps({"permission":"deny","user_message":sys.argv[1],"agent_message":sys.argv[1]}))' "$1"
  exit 0
}

if ! echo "$COMMAND" | grep -Eqi '(^|[[:space:]])git[[:space:]]+(commit|push|merge|rebase)'; then
  allow
fi

# If the command itself switches off a protected branch first, allow
if echo "$COMMAND" | grep -Eqi 'git[[:space:]]+checkout[[:space:]]+(-b|--branch)[[:space:]]+(feature|fix|chore|docs|agent|hotfix)/'; then
  allow
fi

if [[ -n "$CD_PATH" ]]; then
  repo_dir="$CD_PATH"
elif [[ -n "$HOOK_CWD" ]]; then
  repo_dir="$HOOK_CWD"
else
  repo_dir="$(pwd)"
fi

branch="$(git -C "$repo_dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
case "$branch" in
  main|master|develop|release|production)
    deny "Protected-branch hook: refusing git mutation on protected branch '$branch' in $repo_dir. Use a feature/fix branch."
    ;;
esac

allow
