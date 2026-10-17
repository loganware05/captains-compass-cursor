#!/usr/bin/env bash
# run-cycle.sh — Cognitive Core Adaptive Development Loop (C4).
#
# Requires COMPASS_CYCLE_ENABLED=1.
# cycle begin also requires COMPASS_ASSESS_ENABLED=1 (C3 compose).
# Never promotes Skills/Policies, merges, deploys, or grants authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
OBJECTIVE=""
PLAN_ID=""
EXECUTION_ID=""
CHECKPOINT_KEY=""
OUTCOME="success"
RETRIES="0"
NOTES=""
SKILLS=""
COST_UNITS="0"

usage() {
  cat <<'USAGE'
Usage:
  run-cycle.sh begin --objective TEXT [--plan-id ID] [--repo-root PATH]
  run-cycle.sh checkpoint --execution-id ID --checkpoint-key KEY
                 [--outcome TEXT] [--retries N] [--notes TEXT]
                 [--skills CSV] [--cost-units N] [--repo-root PATH]
  run-cycle.sh close --execution-id ID [--outcome success|partial|failed|cancelled]
                 [--repo-root PATH]
  run-cycle.sh review [--repo-root PATH]

Requires COMPASS_CYCLE_ENABLED=1.
begin also requires COMPASS_ASSESS_ENABLED=1.
Advisory only — never mutates authority or auto-promotes.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    begin|checkpoint|close|review)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --objective)
      OBJECTIVE="$2"
      shift 2
      ;;
    --plan-id)
      PLAN_ID="$2"
      shift 2
      ;;
    --execution-id)
      EXECUTION_ID="$2"
      shift 2
      ;;
    --checkpoint-key)
      CHECKPOINT_KEY="$2"
      shift 2
      ;;
    --outcome)
      OUTCOME="$2"
      shift 2
      ;;
    --retries)
      RETRIES="$2"
      shift 2
      ;;
    --notes)
      NOTES="$2"
      shift 2
      ;;
    --skills)
      SKILLS="$2"
      shift 2
      ;;
    --cost-units)
      COST_UNITS="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$CMD" ]]; then
  usage >&2
  exit 2
fi

if [[ "$CMD" == "begin" && -z "$OBJECTIVE" ]]; then
  echo "error: --objective is required for cycle begin" >&2
  usage >&2
  exit 2
fi

if [[ "$CMD" == "checkpoint" || "$CMD" == "close" ]]; then
  if [[ -z "$EXECUTION_ID" ]]; then
    echo "error: --execution-id is required for cycle $CMD" >&2
    usage >&2
    exit 2
  fi
fi

if [[ "$CMD" == "checkpoint" && -z "$CHECKPOINT_KEY" ]]; then
  echo "error: --checkpoint-key is required for cycle checkpoint" >&2
  usage >&2
  exit 2
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$OBJECTIVE" "$PLAN_ID" "$EXECUTION_ID" \
  "$CHECKPOINT_KEY" "$OUTCOME" "$RETRIES" "$NOTES" "$SKILLS" "$COST_UNITS" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
objective = sys.argv[4]
plan_id = sys.argv[5]
execution_id = sys.argv[6]
checkpoint_key = sys.argv[7]
outcome = sys.argv[8]
retries = int(sys.argv[9] or "0")
notes = sys.argv[10]
skills_csv = sys.argv[11]
cost_units = float(sys.argv[12] or "0")

sys.path.insert(0, str(control_root))

from orchestrator.cycle.enabled import cycle_enabled
from orchestrator.cycle.service import (
    CycleServiceError,
    cycle_begin,
    cycle_checkpoint,
    cycle_close,
    learning_review,
)

if not cycle_enabled():
    print(
        "error: COMPASS_CYCLE_ENABLED is unset/off — "
        "set COMPASS_CYCLE_ENABLED=1 to run northstar cycle",
        file=sys.stderr,
    )
    sys.exit(2)

skills = [s.strip() for s in skills_csv.split(",") if s.strip()] if skills_csv else []

try:
    if cmd == "begin":
        result = cycle_begin(
            repo_root,
            objective,
            plan_id=plan_id or None,
        )
    elif cmd == "checkpoint":
        result = cycle_checkpoint(
            repo_root,
            execution_id,
            checkpoint_key=checkpoint_key,
            outcome=outcome or "in_progress",
            retries=retries,
            notes=notes,
            skills=skills,
            cost_units=cost_units,
        )
    elif cmd == "close":
        result = cycle_close(repo_root, execution_id, outcome=outcome or "success")
    elif cmd == "review":
        result = learning_review(repo_root)
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (CycleServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
PY
