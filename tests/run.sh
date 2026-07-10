#!/usr/bin/env bash
# tests/run.sh — Automated installer, doctor, and hook tests for Captain's Compass
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

assert_eq() {
  local name="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name (expected='$expected' actual='$actual')" >&2
    FAIL=$((FAIL + 1))
  fi
}

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

assert_false() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "FAIL: $name (expected failure)" >&2
    FAIL=$((FAIL + 1))
  else
    echo "PASS: $name"
    PASS=$((PASS + 1))
  fi
}

assert_contains() {
  local name="$1" needle="$2" haystack="$3"
  if echo "$haystack" | grep -Eq "$needle"; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name (missing '$needle' in: $haystack)" >&2
    FAIL=$((FAIL + 1))
  fi
}

chmod +x "$ROOT/scripts/install.sh" "$ROOT/scripts/doctor.sh" "$ROOT/.cursor/hooks/"*.sh

echo "=== doctor on control repo ==="
assert_true "doctor passes on control repo" "$ROOT/scripts/doctor.sh" "$ROOT"

echo "=== hook: secret protection ==="
out="$(echo '{"command":"npm test"}' | "$ROOT/.cursor/hooks/secret-protection.sh")"
assert_contains "secret allows npm test" '"permission": ?"allow"|"permission":"allow"' "$out"
out="$(echo '{"command":"git add .env"}' | "$ROOT/.cursor/hooks/secret-protection.sh")"
assert_contains "secret denies git add .env" '"permission": ?"deny"|"permission":"deny"' "$out"

echo "=== hook: protected branch ==="
TMPB="$(mktemp -d "${TMPDIR:-/tmp}/compass-branch-XXXXXX")"
git -C "$TMPB" init -q
git -C "$TMPB" checkout -b feature/hook-test -q 2>/dev/null || true
echo x > "$TMPB/f"
git -C "$TMPB" add f
git -C "$TMPB" -c user.email=t@t.com -c user.name=t commit -q -m init
(
  cd "$TMPB"
  git checkout -B feature/hook-test >/dev/null
  out="$(echo '{"command":"git commit -m x"}' | "$ROOT/.cursor/hooks/protected-branch.sh")"
  echo "$out" > /tmp/compass-hook-feature.out
  git checkout -B main >/dev/null
  out2="$(echo '{"command":"git commit -m x"}' | "$ROOT/.cursor/hooks/protected-branch.sh")"
  echo "$out2" > /tmp/compass-hook-main.out
)
assert_contains "protected allows feature branch" 'allow' "$(cat /tmp/compass-hook-feature.out)"
assert_contains "protected denies main" 'deny' "$(cat /tmp/compass-hook-main.out)"
rm -rf "$TMPB"

echo "=== hook: plan approval ==="
TMPP="$(mktemp -d "${TMPDIR:-/tmp}/compass-plan-XXXXXX")"
cd "$TMPP"
git init -q && git checkout -b feature/plan -q 2>/dev/null || true
echo x > f && git add f && git -c user.email=t@t.com -c user.name=t commit -q -m init
git checkout -B feature/plan >/dev/null

cat > IMPLEMENTATION_PLAN.md <<'PLAN'
# Implementation Plan
## Metadata
- Status: DRAFT
PLAN
out="$(echo '{"path":"src/App.tsx"}' | "$ROOT/.cursor/hooks/plan-approval-check.sh")"
assert_contains "plan denies DRAFT for src" 'deny' "$out"

cat > IMPLEMENTATION_PLAN.md <<'PLAN'
# Implementation Plan
## Metadata
- Status: APPROVED
- Approved by: Captain
- Approval date: 2026-07-10
## Approval Record
Approved.
PLAN
out="$(echo '{"path":"src/App.tsx"}' | "$ROOT/.cursor/hooks/plan-approval-check.sh")"
assert_contains "plan allows APPROVED src on feature" 'allow' "$out"
out="$(echo '{"path":"IMPLEMENTATION_PLAN.md"}' | "$ROOT/.cursor/hooks/plan-approval-check.sh")"
assert_contains "plan allows editing plan file" 'allow' "$out"
cd "$ROOT"
rm -rf "$TMPP"

echo "=== install into temp git repo ==="
TMP="$(mktemp -d "${TMPDIR:-/tmp}/compass-install-XXXXXX")"
cleanup() { rm -rf "$TMP" /tmp/compass-hook-feature.out /tmp/compass-hook-main.out 2>/dev/null || true; }
trap cleanup EXIT

git -C "$TMP" init -q
git -C "$TMP" branch -M main
echo "# fixture" > "$TMP/README.md"
git -C "$TMP" add README.md
git -C "$TMP" -c user.email="test@example.com" -c user.name="Test" commit -q -m "chore: init fixture"

"$ROOT/scripts/install.sh" "$TMP"

assert_true "installed AGENTS.md" test -f "$TMP/AGENTS.md"
assert_true "installed rules" test -f "$TMP/.cursor/rules/01-plan-approval-gate.mdc"
assert_true "installed skill" test -f "$TMP/.cursor/skills/implementation-planning/SKILL.md"
assert_true "installed react skill" test -f "$TMP/.cursor/skills/react-engineering/SKILL.md"
assert_true "installed playwright skill" test -f "$TMP/.cursor/skills/playwright-browser-validation/SKILL.md"
assert_true "installed github skill" test -f "$TMP/.cursor/skills/github-integration/SKILL.md"
assert_true "installed agent" test -f "$TMP/.cursor/agents/repository-scout.md"
assert_true "installed hooks.json" test -f "$TMP/.cursor/hooks.json"
assert_true "installed plan-approval hook" test -x "$TMP/.cursor/hooks/plan-approval-check.sh"
assert_true "created evidence dir" test -d "$TMP/.agent/evidence"
assert_true "wrote COMPASS_VERSION" test -f "$TMP/.agent/COMPASS_VERSION"
assert_eq "version matches" "$(tr -d '[:space:]' < "$ROOT/VERSION")" "$(tr -d '[:space:]' < "$TMP/.agent/COMPASS_VERSION")"

echo "=== doctor on installed product ==="
assert_true "doctor passes on installed product" "$ROOT/scripts/doctor.sh" "$TMP"

echo "=== refuse overwrite without --force ==="
assert_false "second install without --force fails" "$ROOT/scripts/install.sh" "$TMP"

echo "=== --force preserves existing product docs ==="
echo "PRODUCT_MARKER" > "$TMP/PROJECT_CONTEXT.md"
assert_true "install --force succeeds" "$ROOT/scripts/install.sh" --force "$TMP"
assert_contains "force keeps PROJECT_CONTEXT" "PRODUCT_MARKER" "$(cat "$TMP/PROJECT_CONTEXT.md")"
assert_true "force still refreshes skills" test -f "$TMP/.cursor/skills/react-engineering/SKILL.md"

echo "=== refuse non-git target ==="
NON_GIT="$(mktemp -d "${TMPDIR:-/tmp}/compass-nongit-XXXXXX")"
assert_false "non-git target fails" "$ROOT/scripts/install.sh" "$NON_GIT"
rm -rf "$NON_GIT"

echo "=== refuse install into control repo ==="
assert_false "install into self fails" "$ROOT/scripts/install.sh" "$ROOT"

echo
echo "Results: $PASS passed, $FAIL failed"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
