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

chmod +x "$ROOT/scripts/install.sh" "$ROOT/scripts/doctor.sh" "$ROOT/scripts/compile-capability-registry.sh" "$ROOT/.cursor/hooks/"*.sh

echo "=== control repo budget templates + CI ==="
assert_true "budget ledger template in control" test -f "$ROOT/templates/agent/BUDGET_LEDGER.md"
assert_true "budget stop template in control" test -f "$ROOT/templates/agent/BUDGET_STOP_REPORT.md"
assert_true "control CI workflow present" test -f "$ROOT/.github/workflows/ci.yml"
assert_true "autonomy-budget skill in control" test -f "$ROOT/.cursor/skills/autonomy-budget/SKILL.md"
assert_true "evidence matrix in control" test -f "$ROOT/docs/EVIDENCE_MATRIX.md"
assert_true "multi-runtime docs in control" test -f "$ROOT/docs/integrations/multi-runtime-agents.md"
assert_true "plan-feature command in control" test -f "$ROOT/.cursor/commands/plan-feature.md"
assert_true "implement-approved-plan command in control" test -f "$ROOT/.cursor/commands/implement-approved-plan.md"
assert_true "CLAUDE.md template in control" test -f "$ROOT/templates/docs/CLAUDE.md"
assert_true "harness-gc skill in control" test -f "$ROOT/.cursor/skills/harness-gc/SKILL.md"
assert_true "dependency-supply-chain skill in control" test -f "$ROOT/.cursor/skills/dependency-supply-chain/SKILL.md"
assert_true "capability-planning skill in control" test -f "$ROOT/.cursor/skills/capability-planning/SKILL.md"
assert_true "execution-telemetry skill in control" test -f "$ROOT/.cursor/skills/execution-telemetry/SKILL.md"
assert_true "candidate-promotion skill in control" test -f "$ROOT/.cursor/skills/candidate-promotion/SKILL.md"
assert_true "experience-skill-training skill in control" test -f "$ROOT/.cursor/skills/experience-skill-training/SKILL.md"
assert_true "skill-learning-loop skill in control" test -f "$ROOT/.cursor/skills/skill-learning-loop/SKILL.md"
assert_true "compass-evaluator skill in control" test -f "$ROOT/.cursor/skills/compass-evaluator/SKILL.md"
assert_true "experience-routing skill in control" test -f "$ROOT/.cursor/skills/experience-routing/SKILL.md"
assert_true "compass-evaluator agent in control" test -f "$ROOT/.cursor/agents/compass-evaluator.md"
assert_true "capability-plan script in control" test -f "$ROOT/scripts/capability-plan.sh"
assert_true "record-execution-run script in control" test -f "$ROOT/scripts/record-execution-run.sh"
assert_true "promote-candidate script in control" test -f "$ROOT/scripts/promote-candidate.sh"
assert_true "train-skill-from-experience script in control" test -f "$ROOT/scripts/train-skill-from-experience.sh"
assert_true "run-skill-learning-loop script in control" test -f "$ROOT/scripts/run-skill-learning-loop.sh"
assert_true "bridge-learning-experiences script in control" test -f "$ROOT/scripts/bridge-learning-experiences.sh"
assert_true "apply-skill-improvement script in control" test -f "$ROOT/scripts/apply-skill-improvement.sh"
assert_true "experience layout in control" test -f "$ROOT/.agent/experience/.gitkeep"

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

echo "=== hook: branch name ==="
TMPN="$(mktemp -d "${TMPDIR:-/tmp}/compass-branchname-XXXXXX")"
git -C "$TMPN" init -q
echo x > "$TMPN/f"
git -C "$TMPN" add f
git -C "$TMPN" -c user.email=t@t.com -c user.name=t commit -q -m init
(
  cd "$TMPN"
  git checkout -B weird-name >/dev/null 2>&1
  out="$(echo "{\"command\":\"git commit -m x\",\"cwd\":\"$TMPN\"}" | "$ROOT/.cursor/hooks/branch-name-validation.sh")"
  echo "$out" > /tmp/compass-branchname-bad.out
  git checkout -B feature/ok-name >/dev/null
  out2="$(echo "{\"command\":\"git commit -m x\",\"cwd\":\"$TMPN\"}" | "$ROOT/.cursor/hooks/branch-name-validation.sh")"
  echo "$out2" > /tmp/compass-branchname-good.out
)
assert_contains "branch-name denies weird-name" 'deny' "$(cat /tmp/compass-branchname-bad.out)"
assert_contains "branch-name allows feature/*" 'allow' "$(cat /tmp/compass-branchname-good.out)"
rm -rf "$TMPN"

echo "=== hook: pr evidence ==="
TMPE="$(mktemp -d "${TMPDIR:-/tmp}/compass-evidence-XXXXXX")"
git -C "$TMPE" init -q
out="$(echo "{\"command\":\"gh pr create\",\"cwd\":\"$TMPE\"}" | "$ROOT/.cursor/hooks/pr-evidence-validation.sh")"
assert_contains "pr-evidence denies missing plan" 'deny' "$out"
mkdir -p "$TMPE/.agent/evidence"
cat > "$TMPE/IMPLEMENTATION_PLAN.md" <<'PLAN'
# Implementation Plan
## Metadata
- Status: APPROVED
- Approved by: Captain
- Approval date: 2026-07-10
## Approval Record
Approved.
PLAN
echo proof > "$TMPE/.agent/evidence/note.txt"
out="$(echo "{\"command\":\"gh pr create\",\"cwd\":\"$TMPE\"}" | "$ROOT/.cursor/hooks/pr-evidence-validation.sh")"
assert_contains "pr-evidence allows with plan+files" 'allow' "$out"
rm -rf "$TMPE"

echo "=== install into temp git repo ==="
TMP="$(mktemp -d "${TMPDIR:-/tmp}/compass-install-XXXXXX")"
cleanup() { rm -rf "$TMP" /tmp/compass-hook-feature.out /tmp/compass-hook-main.out /tmp/compass-branchname-bad.out /tmp/compass-branchname-good.out 2>/dev/null || true; }
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
assert_true "installed node skill" test -f "$TMP/.cursor/skills/node-engineering/SKILL.md"
assert_true "installed prisma skill" test -f "$TMP/.cursor/skills/postgres-prisma/SKILL.md"
assert_true "installed docker-cloud skill" test -f "$TMP/.cursor/skills/docker-cloud/SKILL.md"
assert_true "installed linear skill" test -f "$TMP/.cursor/skills/linear-integration/SKILL.md"
assert_true "installed notion skill" test -f "$TMP/.cursor/skills/notion-integration/SKILL.md"
assert_true "installed python-ml skill" test -f "$TMP/.cursor/skills/python-ml/SKILL.md"
assert_true "installed ios skill" test -f "$TMP/.cursor/skills/ios-engineering/SKILL.md"
assert_true "installed source-code-context skill" test -f "$TMP/.cursor/skills/source-code-context/SKILL.md"
assert_true "installed code-structure-cleanup skill" test -f "$TMP/.cursor/skills/code-structure-cleanup/SKILL.md"
assert_true "installed review-fix-loop skill" test -f "$TMP/.cursor/skills/review-fix-loop/SKILL.md"
assert_true "installed autonomy-budget skill" test -f "$TMP/.cursor/skills/autonomy-budget/SKILL.md"
assert_true "installed agent" test -f "$TMP/.cursor/agents/repository-scout.md"
assert_true "installed hooks.json" test -f "$TMP/.cursor/hooks.json"
assert_true "installed plan-approval hook" test -x "$TMP/.cursor/hooks/plan-approval-check.sh"
assert_true "installed branch-name hook" test -x "$TMP/.cursor/hooks/branch-name-validation.sh"
assert_true "installed pre-push hook" test -x "$TMP/.cursor/hooks/pre-push-tests.sh"
assert_true "installed pr-evidence hook" test -x "$TMP/.cursor/hooks/pr-evidence-validation.sh"
assert_true "installed hooks common" test -f "$TMP/.cursor/hooks/_common.sh"
assert_true "created evidence dir" test -d "$TMP/.agent/evidence"
assert_true "created budgets dir" test -d "$TMP/.agent/budgets"
assert_true "installed budget ledger template" test -f "$TMP/.agent/budgets/_templates/BUDGET_LEDGER.md"
assert_true "installed budget stop template" test -f "$TMP/.agent/budgets/_templates/BUDGET_STOP_REPORT.md"
assert_true "installed plan-feature command" test -f "$TMP/.cursor/commands/plan-feature.md"
assert_true "installed implement-approved-plan command" test -f "$TMP/.cursor/commands/implement-approved-plan.md"
assert_true "installed validate-change command" test -f "$TMP/.cursor/commands/validate-change.md"
assert_true "installed prepare-pr command" test -f "$TMP/.cursor/commands/prepare-pr.md"
assert_true "installed close-workstream command" test -f "$TMP/.cursor/commands/close-workstream.md"
assert_true "installed initialize-project command" test -f "$TMP/.cursor/commands/initialize-project.md"
assert_true "installed CLAUDE.md adapter" test -f "$TMP/CLAUDE.md"
assert_true "installed evidence matrix doc" test -f "$TMP/docs/EVIDENCE_MATRIX.md"
assert_true "installed multi-runtime doc" test -f "$TMP/docs/integrations/multi-runtime-agents.md"
assert_true "installed technology-intelligence doc" test -f "$TMP/docs/integrations/technology-intelligence.md"
assert_true "installed harness-gc skill" test -f "$TMP/.cursor/skills/harness-gc/SKILL.md"
assert_true "installed dependency-supply-chain skill" test -f "$TMP/.cursor/skills/dependency-supply-chain/SKILL.md"
assert_true "installed capability-planning skill" test -f "$TMP/.cursor/skills/capability-planning/SKILL.md"
assert_true "installed capability-planning sidecar" test -f "$TMP/.cursor/skills/capability-planning/capability.yaml"
assert_true "installed plan template has Required Capabilities" grep -q "## Required Capabilities" "$TMP/IMPLEMENTATION_PLAN.md"
assert_true "created capabilities compiled dir" test -d "$TMP/.agent/capabilities/compiled"
assert_true "created plans dir" test -d "$TMP/.agent/plans"
assert_true "created sessions dir" test -d "$TMP/.agent/sessions"
assert_true "installed session note template" test -f "$TMP/.agent/sessions/_templates/SESSION_NOTE.md"
assert_true "wrote COMPASS_VERSION" test -f "$TMP/.agent/COMPASS_VERSION"
assert_eq "version matches" "$(tr -d '[:space:]' < "$ROOT/VERSION")" "$(tr -d '[:space:]' < "$TMP/.agent/COMPASS_VERSION")"

echo "=== CLAUDE.md not overwritten on force ==="
echo "CUSTOM_CLAUDE" > "$TMP/CLAUDE.md"
assert_true "install --force succeeds" "$ROOT/scripts/install.sh" --force "$TMP"
assert_contains "force keeps customized CLAUDE.md" "CUSTOM_CLAUDE" "$(cat "$TMP/CLAUDE.md")"

echo "=== hooks.json failClosed policy ==="
failclosed_out="$(python3 - "$TMP/.cursor/hooks.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
entries = [e for group in data.get("hooks", {}).values() for e in group]
by_cmd = {e.get("command"): e.get("failClosed") for e in entries}
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
ok = all(by_cmd.get(c) is True for c in critical) and all(by_cmd.get(c) is False for c in soft)
print("ok" if ok else "bad")
for c in critical + soft:
    print(f"{c}={by_cmd.get(c)!r}")
sys.exit(0 if ok else 1)
PY
)" || true
assert_contains "critical hooks failClosed true / soft false" '^ok$' "$(echo "$failclosed_out" | head -n1)"

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

echo "=== update.sh refreshes version ==="
chmod +x "$ROOT/scripts/update.sh" "$ROOT/scripts/uninstall.sh"
echo "0.0.0-test" > "$TMP/.agent/COMPASS_VERSION"
assert_true "update.sh succeeds" "$ROOT/scripts/update.sh" "$TMP"
assert_eq "update wrote new version" "$(tr -d '[:space:]' < "$ROOT/VERSION")" "$(tr -d '[:space:]' < "$TMP/.agent/COMPASS_VERSION")"
assert_true "update kept PROJECT_CONTEXT marker" grep -q "PRODUCT_MARKER" "$TMP/PROJECT_CONTEXT.md"

echo "=== uninstall.sh removes cursor package ==="
assert_true "uninstall requires --yes" bash -c "! '$ROOT/scripts/uninstall.sh' '$TMP' >/dev/null 2>&1"
assert_true "uninstall --yes succeeds" "$ROOT/scripts/uninstall.sh" --yes "$TMP"
assert_true "uninstall removed rules" bash -c "! test -d '$TMP/.cursor/rules'"
assert_true "uninstall kept PROJECT_CONTEXT" test -f "$TMP/PROJECT_CONTEXT.md"

echo "=== orchestrator schema tests ==="
assert_true "orchestrator unittest" bash -c "cd '$ROOT' && PYTHONPATH='$ROOT' python3 -m unittest discover -s tests/orchestrator -p 'test_*.py' -q"

echo "=== capability registry compile ==="
assert_true "registry compiles" "$ROOT/scripts/compile-capability-registry.sh"
assert_true "registry output exists" test -f "$ROOT/.agent/capabilities/compiled/registry.json"

echo "=== capability resolve smoke ==="
chmod +x "$ROOT/scripts/capability-resolve.sh" "$ROOT/scripts/plan-task-graph.sh" "$ROOT/scripts/build-agent-manifests.sh" "$ROOT/scripts/capability-plan.sh"
out="$( "$ROOT/scripts/capability-resolve.sh" "Build a React dashboard" )"
assert_contains "resolve returns react-engineering" 'react-engineering' "$out"

echo "=== task graph planner smoke ==="
graph_out="$( "$ROOT/scripts/plan-task-graph.sh" "Build a React dashboard with tests" )"
assert_contains "planner returns task-discovery" 'task-discovery' "$graph_out"
assert_contains "planner returns task-impl-frontend" 'task-impl-frontend' "$graph_out"

echo "=== agent manifest assembler smoke ==="
manifest_out="$( "$ROOT/scripts/build-agent-manifests.sh" "Build a React dashboard with tests" )"
assert_contains "manifest references implementation-agent" 'implementation-agent' "$manifest_out"
assert_contains "manifest includes react-engineering skill" 'react-engineering' "$manifest_out"

echo "=== capability plan integration smoke ==="
plan_out="$( "$ROOT/scripts/capability-plan.sh" --plan-id smoke-test "Build a React dashboard with tests" )"
assert_contains "plan has Required Capabilities" '## Required Capabilities' "$plan_out"
assert_contains "plan has Task Graph" '## Task Graph' "$plan_out"
assert_contains "plan has Approval Boundary" '## Approval Boundary' "$plan_out"
assert_contains "plan mentions react-engineering" 'react-engineering' "$plan_out"

echo "=== harness evals ==="
assert_true "evals runner passes" "$ROOT/tests/evals/run.sh"

echo "=== refuse install into control repo ==="
assert_false "install into self fails" "$ROOT/scripts/install.sh" "$ROOT"

echo
echo "Results: $PASS passed, $FAIL failed"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
