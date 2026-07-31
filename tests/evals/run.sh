#!/usr/bin/env bash
# tests/evals/run.sh — Deterministic harness sensor evals (no LLM-in-CI).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PASS=0
FAIL=0

assert_true() {
  local name="$1"
  shift
  if "$@"; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name" >&2
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local name="$1" needle="$2" haystack="$3"
  if echo "$haystack" | grep -Eq "$needle"; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name (missing '$needle')" >&2
    FAIL=$((FAIL + 1))
  fi
}

chmod +x "$ROOT/.cursor/hooks/"*.sh "$ROOT/scripts/"*.sh 2>/dev/null || true

echo "=== eval: failClosed policy ==="
out="$(python3 - "$ROOT/.cursor/hooks.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
entries = [e for group in data.get("hooks", {}).values() for e in group]
by = {e.get("command"): e.get("failClosed") for e in entries}
critical = [
  ".cursor/hooks/secret-protection.sh",
  ".cursor/hooks/protected-branch.sh",
  ".cursor/hooks/plan-approval-check.sh",
]
soft = [
  ".cursor/hooks/branch-name-validation.sh",
  ".cursor/hooks/pre-commit-formatting.sh",
  ".cursor/hooks/pre-push-tests.sh",
  ".cursor/hooks/pr-evidence-validation.sh",
]
ok = all(by.get(c) is True for c in critical) and all(by.get(c) is False for c in soft)
print("ok" if ok else "bad")
sys.exit(0 if ok else 1)
PY
)" || true
assert_contains "failClosed critical/soft split" '^ok$' "$(echo "$out" | head -n1)"

echo "=== eval: plan-approval DRAFT vs APPROVED ==="
TMP="$(mktemp -d "${TMPDIR:-/tmp}/compass-eval-XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT
git -C "$TMP" init -q
git -C "$TMP" checkout -b feature/eval -q 2>/dev/null || true
echo x > "$TMP/f"
git -C "$TMP" add f
git -C "$TMP" -c user.email=t@t.com -c user.name=t commit -q -m init
(
  cd "$TMP"
  git checkout -B feature/eval >/dev/null
  cat > IMPLEMENTATION_PLAN.md <<'PLAN'
# Implementation Plan
## Metadata
- Status: DRAFT
PLAN
  out="$(echo '{"path":"src/App.tsx"}' | "$ROOT/.cursor/hooks/plan-approval-check.sh")"
  echo "$out" > /tmp/compass-eval-draft.out
  cat > IMPLEMENTATION_PLAN.md <<'PLAN'
# Implementation Plan
## Metadata
- Status: APPROVED
- Approved by: Captain
- Approval date: 2026-07-30
## Approval Record
Approved.
PLAN
  out2="$(echo '{"path":"src/App.tsx"}' | "$ROOT/.cursor/hooks/plan-approval-check.sh")"
  echo "$out2" > /tmp/compass-eval-approved.out
)
assert_contains "eval denies DRAFT src edit" 'deny' "$(cat /tmp/compass-eval-draft.out)"
assert_contains "eval allows APPROVED src edit" 'allow' "$(cat /tmp/compass-eval-approved.out)"

echo "=== eval: soft-hook command-string skip ==="
skip_out="$(echo '{"command":"COMPASS_SKIP_FORMAT=1 git commit -m x","cwd":"'"$TMP"'"}' | "$ROOT/.cursor/hooks/pre-commit-formatting.sh")"
assert_contains "format skip via command string" 'allow' "$skip_out"
skip_out2="$(echo '{"command":"COMPASS_SKIP_TESTS=1 git push","cwd":"'"$TMP"'"}' | "$ROOT/.cursor/hooks/pre-push-tests.sh")"
assert_contains "tests skip via command string" 'allow' "$skip_out2"
mkdir -p "$TMP/.agent"
touch "$TMP/.agent/COMPASS_SKIP_HOOKS"
skip_out3="$(echo '{"command":"gh pr create","cwd":"'"$TMP"'"}' | "$ROOT/.cursor/hooks/pr-evidence-validation.sh")"
assert_contains "pr-evidence skip via marker file" 'allow' "$skip_out3"
rm -f "$TMP/.agent/COMPASS_SKIP_HOOKS"

echo "=== eval: control assets present ==="
assert_true "harness-gc skill" test -f "$ROOT/.cursor/skills/harness-gc/SKILL.md"
assert_true "dependency-supply-chain skill" test -f "$ROOT/.cursor/skills/dependency-supply-chain/SKILL.md"
assert_true "session note template" test -f "$ROOT/templates/agent/SESSION_NOTE.md"
assert_true "structural-tests example" test -f "$ROOT/examples/structural-tests/README.md"
assert_true "sandbox behavioral checklist" test -f "$ROOT/docs/evals/SANDBOX_BEHAVIORAL_CHECKLIST.md"

echo
echo "Eval results: $PASS passed, $FAIL failed"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
