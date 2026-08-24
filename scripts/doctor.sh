#!/usr/bin/env bash
# doctor.sh — Validate Captain's Compass control repository (or an installed product copy).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ $# -gt 0 ]]; then
  ROOT="$(cd "$1" && pwd)"
fi

errors=0
warnings=0

ok() { echo "  ok: $1"; }
fail() { echo "  FAIL: $1" >&2; errors=$((errors + 1)); }
warn() { echo "  warn: $1" >&2; warnings=$((warnings + 1)); }

echo "Captain's Compass doctor"
echo "Root: $ROOT"
echo

# VERSION
if [[ -f "$ROOT/VERSION" ]]; then
  VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"
  ok "VERSION=$VERSION"
elif [[ -f "$ROOT/.agent/COMPASS_VERSION" ]]; then
  VERSION="$(tr -d '[:space:]' < "$ROOT/.agent/COMPASS_VERSION")"
  ok "COMPASS_VERSION=$VERSION (installed product)"
else
  fail "VERSION or .agent/COMPASS_VERSION missing"
  VERSION="unknown"
fi

# Core docs
for f in AGENTS.md PROJECT_CONTEXT.md IMPLEMENTATION_PLAN.md DECISIONS.md PROGRESS.md TESTING.md CHANGELOG.md; do
  if [[ -f "$ROOT/$f" ]]; then
    ok "$f"
  else
    fail "missing $f"
  fi
done

# Rules
RULES=(
  00-core-operating-model.mdc
  01-plan-approval-gate.mdc
  02-git-worktree-policy.mdc
  03-validation-definition-of-done.mdc
  04-documentation-memory.mdc
)

for r in "${RULES[@]}"; do
  path="$ROOT/.cursor/rules/$r"
  if [[ ! -f "$path" ]]; then
    fail "missing rule $r"
    continue
  fi
  if ! grep -q "alwaysApply: true" "$path"; then
    fail "rule $r missing alwaysApply: true"
  else
    ok "rule $r"
  fi
  if ! grep -q "^---$" "$path"; then
    fail "rule $r missing frontmatter"
  fi
done

# Skills
SKILLS=(
  repository-discovery
  implementation-planning
  worktree-orchestration
  testing-validation
  security-review
  accessibility-review
  pull-request-preparation
  github-integration
  react-engineering
  playwright-browser-validation
  node-engineering
  postgres-prisma
  docker-cloud
  linear-integration
  notion-integration
  python-ml
  ios-engineering
  source-code-context
  code-structure-cleanup
  review-fix-loop
  autonomy-budget
  harness-gc
  dependency-supply-chain
  capability-planning
  execution-telemetry
  candidate-promotion
  experience-skill-training
  compass-evaluator
  experience-routing
  persistent-role-promotion
  bounded-autonomy
  knowledge-steward
  technology-intelligence-live
  procedure-playbooks
  skill-lifecycle
)

for s in "${SKILLS[@]}"; do
  path="$ROOT/.cursor/skills/$s/SKILL.md"
  if [[ ! -f "$path" ]]; then
    fail "missing Skill $s/SKILL.md"
    continue
  fi
  if ! grep -q "^name:" "$path"; then
    fail "Skill $s missing name frontmatter"
  else
    ok "skill $s"
  fi
done

# Agents
AGENTS=(
  repository-scout.md
  architecture-agent.md
  implementation-agent.md
  test-engineer.md
  security-reviewer.md
  accessibility-reviewer.md
  adversarial-reviewer.md
  documentation-agent.md
  compass-evaluator.md
  knowledge-steward.md
)

for a in "${AGENTS[@]}"; do
  path="$ROOT/.cursor/agents/$a"
  if [[ ! -f "$path" ]]; then
    fail "missing agent $a"
  else
    ok "agent $a"
  fi
done

# Hooks (V0.2+)
if [[ -f "$ROOT/.cursor/hooks.json" ]]; then
  ok "hooks.json"
else
  fail "missing .cursor/hooks.json"
fi

HOOK_SCRIPTS=(
  secret-protection.sh
  protected-branch.sh
  plan-approval-check.sh
  branch-name-validation.sh
  pre-commit-formatting.sh
  pre-push-tests.sh
  pr-evidence-validation.sh
)
for h in "${HOOK_SCRIPTS[@]}"; do
  path="$ROOT/.cursor/hooks/$h"
  if [[ ! -f "$path" ]]; then
    fail "missing hook $h"
  elif [[ ! -x "$path" ]]; then
    warn "hook $h is not executable"
    ok "hook $h present"
  else
    ok "hook $h"
  fi
done

if [[ -f "$ROOT/.cursor/hooks/_common.sh" ]]; then
  ok "hooks _common.sh"
else
  warn "hooks _common.sh missing (shared helpers)"
fi

if ! command -v python3 >/dev/null 2>&1; then
  warn "python3 not on PATH (hooks require python3 for JSON)"
fi

# Control-repo-only checks
if [[ -d "$ROOT/templates/docs" ]]; then
  for f in AGENTS.md PROJECT_CONTEXT.md IMPLEMENTATION_PLAN.md DECISIONS.md PROGRESS.md TESTING.md CHANGELOG.md; do
    if [[ -f "$ROOT/templates/docs/$f" ]]; then
      ok "template $f"
    else
      fail "missing template templates/docs/$f"
    fi
  done
  for f in BUDGET_LEDGER.md BUDGET_STOP_REPORT.md SESSION_NOTE.md; do
    if [[ -f "$ROOT/templates/agent/$f" ]]; then
      ok "budget template $f"
    else
      fail "missing template templates/agent/$f"
    fi
  done
  if [[ -f "$ROOT/tests/evals/run.sh" ]]; then
    ok "evals runner"
  else
    fail "missing tests/evals/run.sh"
  fi
  if [[ -f "$ROOT/docs/evals/SANDBOX_BEHAVIORAL_CHECKLIST.md" ]]; then
    ok "sandbox behavioral checklist"
  else
    fail "missing docs/evals/SANDBOX_BEHAVIORAL_CHECKLIST.md"
  fi
  if [[ -f "$ROOT/examples/structural-tests/README.md" ]]; then
    ok "structural-tests example"
  else
    fail "missing examples/structural-tests/README.md"
  fi
  ORCHESTRATOR_SCHEMAS=(
    capability.schema.json
    task.schema.json
    agent-manifest.schema.json
    model-profile.schema.json
    candidate-capability.schema.json
    execution-run.schema.json
    experience.schema.json
  )
  for s in "${ORCHESTRATOR_SCHEMAS[@]}"; do
    if [[ -f "$ROOT/orchestrator/schemas/$s" ]]; then
      ok "orchestrator schema $s"
    else
      fail "missing orchestrator/schemas/$s"
    fi
  done
  if [[ -f "$ROOT/orchestrator/model_profiles/catalog.json" ]]; then
    ok "orchestrator model catalog"
  else
    fail "missing orchestrator/model_profiles/catalog.json"
  fi
  if command -v python3 >/dev/null 2>&1; then
    if PYTHONPATH="$ROOT" python3 -c "from orchestrator.model_profiles import load_catalog; load_catalog()" 2>/dev/null; then
      ok "orchestrator catalog validates"
    else
      fail "orchestrator catalog validation failed"
    fi
    if "$ROOT/scripts/compile-capability-registry.sh" >/dev/null 2>&1; then
      ok "capability registry compiles"
    else
      fail "capability registry compile failed"
    fi
  else
    warn "skip orchestrator catalog validation (no python3)"
  fi
  if [[ -f "$ROOT/scripts/capability-plan.sh" ]]; then
    ok "scripts/capability-plan.sh present"
  else
    fail "missing scripts/capability-plan.sh"
  fi
  if [[ -f "$ROOT/.cursor/skills/capability-planning/capability.yaml" ]]; then
    ok "capability-planning sidecar"
  else
    fail "missing capability-planning/capability.yaml"
  fi
  if [[ -f "$ROOT/.agent/experience/.gitkeep" ]]; then
    ok ".agent/experience layout"
  else
    fail "missing .agent/experience/.gitkeep"
  fi
  if [[ -f "$ROOT/scripts/record-execution-run.sh" ]]; then
    ok "scripts/record-execution-run.sh present"
  else
    fail "missing scripts/record-execution-run.sh"
  fi
  if [[ -f "$ROOT/.agent/evaluations/.gitkeep" ]]; then
    ok ".agent/evaluations layout"
  else
    fail "missing .agent/evaluations/.gitkeep"
  fi
  if [[ -f "$ROOT/scripts/run-evaluation.sh" ]]; then
    ok "scripts/run-evaluation.sh present"
  else
    fail "missing scripts/run-evaluation.sh"
  fi
  if [[ -f "$ROOT/.agent/routing/proposals/.gitkeep" ]]; then
    ok ".agent/routing/proposals layout"
  else
    fail "missing .agent/routing/proposals/.gitkeep"
  fi
  if [[ -f "$ROOT/.agent/routing/applied/.gitkeep" ]]; then
    ok ".agent/routing/applied layout"
  else
    fail "missing .agent/routing/applied/.gitkeep"
  fi
  if [[ -f "$ROOT/.agent/agents/proficiency/.gitkeep" ]]; then
    ok ".agent/agents/proficiency layout"
  else
    fail "missing .agent/agents/proficiency/.gitkeep"
  fi
  if [[ -f "$ROOT/.agent/agents/promotions/.gitkeep" ]]; then
    ok ".agent/agents/promotions layout"
  else
    fail "missing .agent/agents/promotions/.gitkeep"
  fi
  if [[ -f "$ROOT/orchestrator/matcher/weights.json" ]]; then
    ok "matcher weights.json"
  else
    fail "missing orchestrator/matcher/weights.json"
  fi
  if [[ -x "$ROOT/scripts/propose-persistent-role.sh" ]]; then
    ok "propose-persistent-role.sh"
  else
    fail "missing executable scripts/propose-persistent-role.sh"
  fi
  if [[ -x "$ROOT/scripts/apply-routing-proposal.sh" ]]; then
    ok "apply-routing-proposal.sh"
  else
    fail "missing executable scripts/apply-routing-proposal.sh"
  fi
  if [[ -f "$ROOT/.agent/knowledge/.gitkeep" ]]; then
    ok ".agent/knowledge layout"
  else
    fail "missing .agent/knowledge/.gitkeep"
  fi
  if [[ -x "$ROOT/scripts/ingest-knowledge.sh" ]]; then
    ok "ingest-knowledge.sh"
  else
    fail "missing executable scripts/ingest-knowledge.sh"
  fi
  if [[ -x "$ROOT/scripts/query-knowledge.sh" ]]; then
    ok "query-knowledge.sh"
  else
    fail "missing executable scripts/query-knowledge.sh"
  fi
  if [[ -x "$ROOT/scripts/rebuild-knowledge-vector-index.sh" ]]; then
    ok "rebuild-knowledge-vector-index.sh"
  else
    fail "missing executable scripts/rebuild-knowledge-vector-index.sh"
  fi
  if [[ -x "$ROOT/scripts/refresh-ti-cache.sh" ]]; then
    ok "refresh-ti-cache.sh"
  else
    fail "missing executable scripts/refresh-ti-cache.sh"
  fi
  if [[ -f "$ROOT/.agent/intelligence/.gitkeep" ]]; then
    ok ".agent/intelligence layout"
  else
    fail "missing .agent/intelligence/.gitkeep"
  fi
  if [[ -f "$ROOT/.agent/capabilities/compiled/.gitkeep" ]]; then
    ok ".agent/capabilities/compiled layout"
  else
    fail "missing .agent/capabilities/compiled/.gitkeep"
  fi
  if [[ -d "$ROOT/tests/fixtures/planning" ]]; then
    fixture_count="$(find "$ROOT/tests/fixtures/planning" -maxdepth 1 -name '*.json' | wc -l | tr -d ' ')"
    if [[ "$fixture_count" -ge 6 ]]; then
      ok "planning fixtures ($fixture_count)"
    else
      fail "expected at least 6 planning fixtures, found $fixture_count"
    fi
  else
    fail "missing tests/fixtures/planning"
  fi
  if [[ -f "$ROOT/.github/workflows/ci.yml" ]]; then
    ok "control CI workflow"
  else
    fail "missing .github/workflows/ci.yml"
  fi
  COMMANDS=(
    initialize-project.md
    plan-feature.md
    implement-approved-plan.md
    validate-change.md
    prepare-pr.md
    close-workstream.md
  )
  for c in "${COMMANDS[@]}"; do
    if [[ -f "$ROOT/.cursor/commands/$c" ]]; then
      ok "command $c"
    else
      fail "missing command .cursor/commands/$c"
    fi
  done
  if [[ -f "$ROOT/docs/EVIDENCE_MATRIX.md" ]]; then
    ok "docs/EVIDENCE_MATRIX.md"
  else
    fail "missing docs/EVIDENCE_MATRIX.md"
  fi
  if [[ -f "$ROOT/docs/integrations/multi-runtime-agents.md" ]]; then
    ok "docs/integrations/multi-runtime-agents.md"
  else
    fail "missing docs/integrations/multi-runtime-agents.md"
  fi
  if [[ -f "$ROOT/docs/integrations/technology-intelligence.md" ]]; then
    ok "docs/integrations/technology-intelligence.md"
  else
    fail "missing docs/integrations/technology-intelligence.md"
  fi
  if [[ -f "$ROOT/orchestrator/providers/technology_intelligence/validate.py" ]]; then
    ok "TI candidate validation"
  else
    fail "missing orchestrator/providers/technology_intelligence/validate.py"
  fi
  if [[ -f "$ROOT/templates/docs/CLAUDE.md" ]]; then
    ok "template CLAUDE.md"
  else
    fail "missing templates/docs/CLAUDE.md"
  fi
  if [[ -f "$ROOT/.cursor/hooks.json" ]]; then
    if command -v python3 >/dev/null 2>&1; then
      if python3 - "$ROOT/.cursor/hooks.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
critical = {
    ".cursor/hooks/secret-protection.sh": True,
    ".cursor/hooks/protected-branch.sh": True,
    ".cursor/hooks/plan-approval-check.sh": True,
}
soft = {
    ".cursor/hooks/branch-name-validation.sh": False,
    ".cursor/hooks/pre-commit-formatting.sh": False,
    ".cursor/hooks/pre-push-tests.sh": False,
    ".cursor/hooks/pr-evidence-validation.sh": False,
}
entries = []
for group in data.get("hooks", {}).values():
    for item in group:
        entries.append(item)
by_cmd = {e.get("command"): e.get("failClosed") for e in entries}
errors = []
for cmd, expected in critical.items():
    if by_cmd.get(cmd) is not True:
        errors.append(f"{cmd} expected failClosed true got {by_cmd.get(cmd)!r}")
for cmd, expected in soft.items():
    if by_cmd.get(cmd) is not False:
        errors.append(f"{cmd} expected failClosed false got {by_cmd.get(cmd)!r}")
if errors:
    print("; ".join(errors))
    sys.exit(1)
PY
      then
        ok "hooks.json failClosed policy"
      else
        fail "hooks.json failClosed policy"
      fi
    else
      warn "skip failClosed policy check (no python3)"
    fi
  fi
  if [[ -x "$ROOT/scripts/install.sh" || -f "$ROOT/scripts/install.sh" ]]; then
    ok "scripts/install.sh present"
  else
    fail "scripts/install.sh missing"
  fi
  if [[ -f "$ROOT/scripts/doctor.sh" ]]; then
    ok "scripts/doctor.sh present"
  else
    fail "scripts/doctor.sh missing"
  fi
  if [[ -f "$ROOT/scripts/update.sh" ]]; then
    ok "scripts/update.sh present"
  else
    fail "scripts/update.sh missing"
  fi
  if [[ -f "$ROOT/scripts/uninstall.sh" ]]; then
    ok "scripts/uninstall.sh present"
  else
    fail "scripts/uninstall.sh missing"
  fi
fi

# Installed product: budgets directory expected after install/update
if [[ -f "$ROOT/.agent/COMPASS_VERSION" ]]; then
  if [[ -d "$ROOT/.agent/budgets" ]]; then
    ok ".agent/budgets directory"
  else
    fail "missing .agent/budgets (re-run update/install)"
  fi
fi

echo
if [[ "$errors" -gt 0 ]]; then
  echo "Doctor failed: $errors error(s), $warnings warning(s)"
  exit 1
fi

echo "Doctor passed: 0 errors, $warnings warning(s)"
exit 0
