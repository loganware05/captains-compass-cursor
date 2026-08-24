#!/usr/bin/env bash
# run-evaluation.sh — Record a bounded Captain Compass Evaluator experiment.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAN_ID=""
OBJECTIVE=""
ALTERNATIVES=""
RECOMMENDATION=""
WINNER=""
HYPOTHESIS=""
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: run-evaluation.sh --plan-id ID --objective TEXT --alternatives JSON --recommendation TEXT

--alternatives must be a JSON array of objects with id and label (min 2).
Optional: --winner ID --hypothesis TEXT --repo-root PATH
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --objective) OBJECTIVE="$2"; shift 2 ;;
    --alternatives) ALTERNATIVES="$2"; shift 2 ;;
    --recommendation) RECOMMENDATION="$2"; shift 2 ;;
    --winner) WINNER="$2"; shift 2 ;;
    --hypothesis) HYPOTHESIS="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$PLAN_ID" || -z "$OBJECTIVE" || -z "$ALTERNATIVES" || -z "$RECOMMENDATION" ]]; then
  echo "error: --plan-id, --objective, --alternatives, and --recommendation are required" >&2
  usage >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$PLAN_ID" "$OBJECTIVE" "$ALTERNATIVES" "$RECOMMENDATION" "$WINNER" "$HYPOTHESIS" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.evaluator.record import record_evaluation

repo = Path(sys.argv[1]).resolve()
plan_id = sys.argv[2]
objective = sys.argv[3]
alternatives = json.loads(sys.argv[4])
recommendation = sys.argv[5]
winner = sys.argv[6]
hypothesis = sys.argv[7]
path = record_evaluation(
    repo,
    plan_id=plan_id,
    objective=objective,
    alternatives=alternatives,
    recommendation=recommendation,
    winner_alternative_id=winner,
    hypothesis=hypothesis,
)
print(json.dumps({"evaluation": str(path)}, indent=2))
PY
