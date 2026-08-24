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
assert_true "capability-planning skill" test -f "$ROOT/.cursor/skills/capability-planning/SKILL.md"
assert_true "execution-telemetry skill" test -f "$ROOT/.cursor/skills/execution-telemetry/SKILL.md"
assert_true "candidate-promotion skill" test -f "$ROOT/.cursor/skills/candidate-promotion/SKILL.md"
assert_true "experience-skill-training skill" test -f "$ROOT/.cursor/skills/experience-skill-training/SKILL.md"
assert_true "compass-evaluator skill" test -f "$ROOT/.cursor/skills/compass-evaluator/SKILL.md"
assert_true "experience-routing skill" test -f "$ROOT/.cursor/skills/experience-routing/SKILL.md"
assert_true "compass-evaluator agent" test -f "$ROOT/.cursor/agents/compass-evaluator.md"
assert_true "capability-plan.sh" test -x "$ROOT/scripts/capability-plan.sh"
assert_true "record-execution-run.sh" test -x "$ROOT/scripts/record-execution-run.sh"
assert_true "run-evaluation.sh" test -x "$ROOT/scripts/run-evaluation.sh"
assert_true "propose-experience-routing.sh" test -x "$ROOT/scripts/propose-experience-routing.sh"
assert_true "technology-intelligence doc" test -f "$ROOT/docs/integrations/technology-intelligence.md"
assert_true "experience.schema.json" test -f "$ROOT/orchestrator/schemas/experience.schema.json"
assert_true "evaluation.schema.json" test -f "$ROOT/orchestrator/schemas/evaluation.schema.json"
template="$ROOT/templates/docs/IMPLEMENTATION_PLAN.md"
assert_contains "template has Required Capabilities" '## Required Capabilities' "$(cat "$template")"
assert_contains "template has Task Graph" '## Task Graph' "$(cat "$template")"
assert_contains "template has Proposed Agent Configuration" '## Proposed Agent Configuration' "$(cat "$template")"
assert_contains "template has Approval Boundary" '## Approval Boundary' "$(cat "$template")"

echo "=== eval: orchestrator schemas present ==="
for schema in capability.schema.json task.schema.json agent-manifest.schema.json; do
  assert_true "schema $schema" test -f "$ROOT/orchestrator/schemas/$schema"
done

echo "=== eval: stub TI provider isolation ==="
stub_out="$(PYTHONPATH="$ROOT" python3 - "$ROOT" <<'PY'
import os
import sys
from pathlib import Path
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections

os.environ.pop("COMPASS_TI_PROVIDER", None)
root = Path(sys.argv[1])
artifacts = build_capability_plan(root, "Build a React dashboard", plan_id="eval-stub-ti")
markdown = render_capability_plan_sections(artifacts)
assert artifacts.technology_intelligence_candidates == []
assert "NOT APPROVED FOR EXECUTION" in markdown
assert "stub" in markdown.lower()
print("ok")
PY
)"
assert_contains "stub TI returns no candidates" '^ok$' "$stub_out"

echo "=== eval: file TI provider isolation ==="
file_out="$(COMPASS_TI_PROVIDER=file PYTHONPATH="$ROOT" python3 - "$ROOT" <<'PY'
import os
import sys
from pathlib import Path
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections

assert os.environ.get("COMPASS_TI_PROVIDER") == "file"
root = Path(sys.argv[1])
artifacts = build_capability_plan(root, "accessible forms", plan_id="eval-file-ti")
markdown = render_capability_plan_sections(artifacts)
assert len(artifacts.technology_intelligence_candidates) >= 1
assert "NOT APPROVED FOR EXECUTION" in markdown
assert "stars-redacted" in markdown
for c in artifacts.technology_intelligence_candidates:
    assert c.get("approved_for_execution") is False
print("ok")
PY
)"
assert_contains "file TI returns redacted candidates" '^ok$' "$file_out"

echo "=== eval: routing proposal does not mutate weights ==="
route_out="$(PYTHONPATH="$ROOT" python3 - "$ROOT" <<'PY'
import sys
from pathlib import Path
from orchestrator.matcher.score import WEIGHTS
from orchestrator.routing.propose import build_routing_proposal, load_experiences

root = Path(sys.argv[1])
before = dict(WEIGHTS)
experiences = load_experiences([root / "tests" / "fixtures" / "experience" / "contact-counter.json"])
proposal = build_routing_proposal(experiences)
assert proposal["auto_apply"] is False
assert dict(WEIGHTS) == before
print("ok")
PY
)"
assert_contains "routing proposal leaves WEIGHTS unchanged" '^ok$' "$route_out"

echo "=== eval: record-execution-run smoke ==="
SMOKE="$(mktemp -d "${TMPDIR:-/tmp}/compass-telemetry-XXXXXX")"
mkdir -p "$SMOKE/.agent/runs" "$SMOKE/.agent/experience"
smoke_out="$("$ROOT/scripts/record-execution-run.sh" \
  --plan-id eval-smoke \
  --outcome success \
  --objective "eval smoke" \
  --skills "execution-telemetry" \
  --repo-root "$SMOKE" 2>&1)"
assert_contains "record-execution-run writes experience" 'experience' "$smoke_out"
assert_true "smoke run json exists" test -n "$(find "$SMOKE/.agent/runs" -name '*.json' | head -1)"
assert_true "smoke experience json exists" test -n "$(find "$SMOKE/.agent/experience" -name '*.json' | head -1)"
rm -rf "$SMOKE"

echo "=== eval: golden fixture determinism ==="
golden_out="$(PYTHONPATH="$ROOT" python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path
from orchestrator.plan_writer.build import build_capability_plan

root = Path(sys.argv[1])
fixtures = root / "tests" / "fixtures" / "planning"
for path in sorted(fixtures.glob("*.json")):
    fixture = json.loads(path.read_text(encoding="utf-8"))
    objective = fixture["objective"]
    context = fixture.get("context", {})
    plan_id = f"eval-{path.stem}"
    first = build_capability_plan(root, objective, context, plan_id=plan_id)
    second = build_capability_plan(root, objective, context, plan_id=plan_id)
    assert first.resolve == second.resolve, path.name
    assert first.task_graph == second.task_graph, path.name
print("ok")
PY
)"
assert_contains "golden fixtures deterministic" '^ok$' "$golden_out"

echo
echo "Eval results: $PASS passed, $FAIL failed"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
