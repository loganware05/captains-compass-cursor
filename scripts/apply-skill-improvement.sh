#!/usr/bin/env bash
# apply-skill-improvement.sh — Captain-gated apply of a skill-improvement-proposal (M20).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
PROPOSAL=""
CAPTAIN_APPROVED=0
APPLY_LIVE=0

usage() {
  cat <<'USAGE'
Usage: apply-skill-improvement.sh --proposal PATH --captain-approved [--apply-live]

Default: write improved SKILL.md under skill-drafts/<slug>-from-learning/.
--apply-live also appends the learned section to the live Skill (Captain only).
Never auto-applies; never sets approved_for_execution.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --proposal) PROPOSAL="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --captain-approved) CAPTAIN_APPROVED=1; shift ;;
    --apply-live) APPLY_LIVE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$PROPOSAL" ]]; then
  echo "error: --proposal is required" >&2
  exit 1
fi
if [[ "$CAPTAIN_APPROVED" -ne 1 ]]; then
  echo "error: --captain-approved is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$PROPOSAL" "$CAPTAIN_APPROVED" "$APPLY_LIVE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.learning.apply_improvement import (
    ImprovementApplyError,
    apply_skill_improvement_proposal,
)

control = Path(sys.argv[1]).resolve()
repo = Path(sys.argv[2]).resolve()
proposal = Path(sys.argv[3]).resolve()
captain = sys.argv[4] == "1"
apply_live = sys.argv[5] == "1"
try:
    result = apply_skill_improvement_proposal(
        repo,
        proposal,
        captain_approved=captain,
        apply_live=apply_live,
        control_root=control,
    )
except ImprovementApplyError as exc:
    print(json.dumps({"error": str(exc)}, indent=2))
    raise SystemExit(1) from exc
print(json.dumps(result, indent=2))
PY
