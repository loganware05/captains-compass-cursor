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
fi

echo
if [[ "$errors" -gt 0 ]]; then
  echo "Doctor failed: $errors error(s), $warnings warning(s)"
  exit 1
fi

echo "Doctor passed: 0 errors, $warnings warning(s)"
exit 0
