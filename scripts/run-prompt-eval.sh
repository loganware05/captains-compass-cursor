#!/usr/bin/env bash
# run-prompt-eval.sh — Hermetic baseline-vs-candidate prompt evaluation (M49).
#
# Requires COMPASS_PROMPT_EVAL_ENABLED=1. Never activates Policies or writes
# live .cursor/ guidance / Skills / routing / authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
EXPORT_FORMAT=""
EXPORT_PATH=""
CASES_PATH=""
AGENT=""
SKILL_ID=""
TASK_TYPE=""
MODEL_HINT=""
REPORT_ID=""

usage() {
  cat <<'USAGE'
Usage:
  run-prompt-eval.sh run [--cases PATH] [--repo-root PATH]
  run-prompt-eval.sh compare [--agent NAME] [--skill-id ID] [--task-type TYPE] [--model-hint ID] [--cases PATH] [--repo-root PATH]
  run-prompt-eval.sh export --format csv [--out PATH] [--report-id ID] [--repo-root PATH]

Requires COMPASS_PROMPT_EVAL_ENABLED=1.
Eval/proposal-only: never activates Policies or mutates .cursor/Skills/routing/authority.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    run|compare|export)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --cases)
      CASES_PATH="$2"
      shift 2
      ;;
    --format)
      EXPORT_FORMAT="$2"
      shift 2
      ;;
    --out)
      EXPORT_PATH="$2"
      shift 2
      ;;
    --agent)
      AGENT="$2"
      shift 2
      ;;
    --skill-id)
      SKILL_ID="$2"
      shift 2
      ;;
    --task-type)
      TASK_TYPE="$2"
      shift 2
      ;;
    --model-hint)
      MODEL_HINT="$2"
      shift 2
      ;;
    --report-id)
      REPORT_ID="$2"
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

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$EXPORT_FORMAT" "$EXPORT_PATH" \
  "$CASES_PATH" "$AGENT" "$SKILL_ID" "$TASK_TYPE" "$MODEL_HINT" "$REPORT_ID" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
export_format = sys.argv[4]
export_path = sys.argv[5]
cases_path = sys.argv[6]
agent = sys.argv[7]
skill_id = sys.argv[8]
task_type = sys.argv[9]
model_hint = sys.argv[10]
report_id = sys.argv[11]

sys.path.insert(0, str(control_root))

from orchestrator.behavior.enabled import prompt_eval_enabled
from orchestrator.behavior.prompt_eval.service import (
    PromptEvalServiceError,
    compare_bundles,
    export_report_csv,
    run_harness,
)

if not prompt_eval_enabled():
    print(
        "error: COMPASS_PROMPT_EVAL_ENABLED is unset/off — "
        "set COMPASS_PROMPT_EVAL_ENABLED=1 to run northstar prompt-eval",
        file=sys.stderr,
    )
    sys.exit(2)

cases = Path(cases_path) if cases_path else None

try:
    if cmd == "run":
        result = run_harness(
            repo_root,
            cases_path=cases,
            control_root=control_root,
        )
    elif cmd == "compare":
        result = compare_bundles(
            repo_root,
            agent=agent,
            skill_id=skill_id,
            task_type=task_type,
            model_hint=model_hint,
            cases_path=cases,
            control_root=control_root,
        )
    elif cmd == "export":
        if export_format and export_format != "csv":
            print("error: only --format csv is supported", file=sys.stderr)
            sys.exit(2)
        dest = Path(export_path) if export_path else (
            repo_root
            / ".agent"
            / "evaluations"
            / "behavior"
            / "prompt-eval"
            / "export.csv"
        )
        path = export_report_csv(repo_root, dest, report_id=report_id)
        result = {"status": "exported", "path": str(path), "canonical_unchanged": True}
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (PromptEvalServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True, default=str))
# Non-zero exit when harness reports non-regression failure
if cmd == "run" and result.get("report", {}).get("non_regression") == "fail":
    sys.exit(1)
PY
