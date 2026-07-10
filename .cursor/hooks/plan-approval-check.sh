#!/usr/bin/env bash
# Before Write/StrReplace on product source, require APPROVED IMPLEMENTATION_PLAN.md
# and a non-protected branch. Planning docs and workflow files are exempt.
set -euo pipefail

input="$(cat)"

FILE_PATH="$(printf '%s' "$input" | python3 -c '
import json, sys
d = json.load(sys.stdin)
path = (
    d.get("file_path")
    or d.get("path")
    or (d.get("tool_input") or {}).get("path")
    or (d.get("input") or {}).get("path")
    or ""
)
if not path and isinstance(d.get("arguments"), dict):
    path = d["arguments"].get("path") or d["arguments"].get("file_path") or ""
print(path)
')"

allow() { echo '{"permission":"allow"}'; exit 0; }

deny() {
  local msg="$1"
  python3 -c 'import json,sys; print(json.dumps({"permission":"deny","user_message":sys.argv[1],"agent_message":sys.argv[1]}))' "$msg"
  exit 0
}

if [[ -z "$FILE_PATH" ]]; then
  allow
fi

rel="${FILE_PATH#./}"

case "$rel" in
  IMPLEMENTATION_PLAN.md|AGENTS.md|PROJECT_CONTEXT.md|DECISIONS.md|PROGRESS.md|TESTING.md|CHANGELOG.md|README.md|LICENSE|VERSION|.gitignore|.cursorignore)
    allow ;;
esac

case "$rel" in
  .cursor/*|.agent/*|docs/*|templates/*|scripts/*|tests/*)
    allow ;;
esac

# Allow non-product markdown
if [[ "$rel" == *.md ]]; then
  allow
fi

# Only gate common product source / config extensions
if ! echo "$rel" | grep -Eq '\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|swift|java|kt|css|scss|sass|html|vue|svelte|json|yml|yaml|toml|sql|prisma)$'; then
  allow
fi

if [[ ! -f IMPLEMENTATION_PLAN.md ]]; then
  deny "Plan-approval hook: IMPLEMENTATION_PLAN.md is missing. Create a plan and get Captain approval before changing product files ($rel)."
fi

status_line="$(grep -E '^- Status:' IMPLEMENTATION_PLAN.md | head -1 || true)"
if ! echo "$status_line" | grep -Eqi 'APPROVED|IN PROGRESS|VALIDATING|COMPLETE'; then
  deny "Plan-approval hook: IMPLEMENTATION_PLAN.md is not APPROVED (found: ${status_line:-none}). Stop and await Captain approval before editing $rel."
fi

if ! grep -Eqi 'Approved by:|Approval date:|## Approval Record' IMPLEMENTATION_PLAN.md; then
  deny "Plan-approval hook: IMPLEMENTATION_PLAN.md lacks an approval record. Record Captain approval before editing $rel."
fi

branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
case "$branch" in
  main|master|develop|release|production)
    deny "Plan-approval hook: refuse product edits on protected branch '$branch'. Create a feature/fix branch first."
    ;;
esac

allow
