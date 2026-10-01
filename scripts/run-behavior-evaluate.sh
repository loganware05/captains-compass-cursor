#!/usr/bin/env bash
# run-behavior-evaluate.sh — Observe-only behavior evaluation (M46).
#
# Requires COMPASS_BEHAVIOR_EVAL_ENABLED=1. Never mutates routing/Skills/authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
EXECUTION_ID=""
EVALUATION_ID=""
EXPORT_FORMAT=""
EXPORT_PATH=""
FORCE=0

usage() {
  cat <<'USAGE'
Usage:
  run-behavior-evaluate.sh pending [--repo-root PATH]
  run-behavior-evaluate.sh run <execution-id> [--repo-root PATH] [--force]
  run-behavior-evaluate.sh review [--repo-root PATH]
  run-behavior-evaluate.sh retry <evaluation-id> [--repo-root PATH]
  run-behavior-evaluate.sh export --format csv [--out PATH] [--repo-root PATH]

Requires COMPASS_BEHAVIOR_EVAL_ENABLED=1.
Observe-only: never mutates routing, Skills, instructions, or authority.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    pending|run|review|retry|export)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --format)
      EXPORT_FORMAT="$2"
      shift 2
      ;;
    --out)
      EXPORT_PATH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$EXECUTION_ID" && "$CMD" == "run" ]]; then
        EXECUTION_ID="$1"
        shift
      elif [[ -z "$EVALUATION_ID" && "$CMD" == "retry" ]]; then
        EVALUATION_ID="$1"
        shift
      else
        echo "error: unknown argument: $1" >&2
        usage >&2
        exit 2
      fi
      ;;
  esac
done

if [[ -z "$CMD" ]]; then
  usage >&2
  exit 2
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$EXECUTION_ID" "$EVALUATION_ID" "$EXPORT_FORMAT" "$EXPORT_PATH" "$FORCE" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
execution_id = sys.argv[4]
evaluation_id = sys.argv[5]
export_format = sys.argv[6]
export_path = sys.argv[7]
force = sys.argv[8] == "1"

sys.path.insert(0, str(control_root))

from orchestrator.behavior.enabled import behavior_eval_enabled
from orchestrator.behavior.service import (
    BehaviorEvalServiceError,
    evaluate_execution,
    evaluate_pending,
    export_ledger_csv,
    retry_evaluation,
    review_ledger,
)

if not behavior_eval_enabled():
    print(
        "error: COMPASS_BEHAVIOR_EVAL_ENABLED is unset/off — "
        "set COMPASS_BEHAVIOR_EVAL_ENABLED=1 to run northstar evaluate",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "pending":
        result = evaluate_pending(repo_root)
    elif cmd == "run":
        if not execution_id:
            print("error: execution-id required for run", file=sys.stderr)
            sys.exit(2)
        result = evaluate_execution(repo_root, execution_id, force=force)
    elif cmd == "review":
        result = review_ledger(repo_root)
    elif cmd == "retry":
        if not evaluation_id:
            print("error: evaluation-id required for retry", file=sys.stderr)
            sys.exit(2)
        result = retry_evaluation(repo_root, evaluation_id)
    elif cmd == "export":
        if export_format and export_format != "csv":
            print("error: only --format csv is supported", file=sys.stderr)
            sys.exit(2)
        dest = Path(export_path) if export_path else (
            repo_root / ".agent" / "evaluations" / "behavior" / "export.csv"
        )
        path = export_ledger_csv(repo_root, dest)
        result = {"status": "exported", "path": str(path), "canonical_unchanged": True}
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (BehaviorEvalServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True, default=str))
PY
