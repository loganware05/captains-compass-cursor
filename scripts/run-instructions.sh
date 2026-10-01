#!/usr/bin/env bash
# run-instructions.sh — Proposal-only instruction registry + PICCO composer (M48).
#
# Requires COMPASS_INSTRUCTIONS_ENABLED=1. Never activates Policies or writes
# live .cursor/ guidance / Skills / routing / authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
INSTRUCTION_ID=""
EXPORT_FORMAT=""
EXPORT_PATH=""
AGENT=""
SKILL_ID=""
TASK_TYPE=""
MODEL_HINT=""

usage() {
  cat <<'USAGE'
Usage:
  run-instructions.sh list [--repo-root PATH]
  run-instructions.sh show <instruction-id> [--repo-root PATH]
  run-instructions.sh compose [--agent NAME] [--skill-id ID] [--task-type TYPE] [--model-hint ID] [--repo-root PATH]
  run-instructions.sh draft-from-candidates [--repo-root PATH]
  run-instructions.sh export --format csv [--out PATH] [--repo-root PATH]

Requires COMPASS_INSTRUCTIONS_ENABLED=1.
Proposal-only: never activates Policies or mutates .cursor/Skills/routing/authority.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    list|show|compose|draft-from-candidates|export)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
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
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$INSTRUCTION_ID" && "$CMD" == "show" ]]; then
        INSTRUCTION_ID="$1"
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
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$INSTRUCTION_ID" "$EXPORT_FORMAT" "$EXPORT_PATH" \
  "$AGENT" "$SKILL_ID" "$TASK_TYPE" "$MODEL_HINT" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
instruction_id = sys.argv[4]
export_format = sys.argv[5]
export_path = sys.argv[6]
agent = sys.argv[7]
skill_id = sys.argv[8]
task_type = sys.argv[9]
model_hint = sys.argv[10]

sys.path.insert(0, str(control_root))

from orchestrator.behavior.enabled import instructions_enabled
from orchestrator.behavior.instructions.service import (
    InstructionServiceError,
    compose,
    draft_candidates,
    export_instructions_csv,
    list_registry,
    show_instruction,
)

if not instructions_enabled():
    print(
        "error: COMPASS_INSTRUCTIONS_ENABLED is unset/off — "
        "set COMPASS_INSTRUCTIONS_ENABLED=1 to run northstar instructions",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "list":
        result = list_registry(repo_root)
    elif cmd == "show":
        if not instruction_id:
            print("error: instruction-id required for show", file=sys.stderr)
            sys.exit(2)
        result = show_instruction(repo_root, instruction_id)
    elif cmd == "compose":
        result = compose(
            repo_root,
            agent=agent,
            skill_id=skill_id,
            task_type=task_type,
            model_hint=model_hint,
        )
    elif cmd == "draft-from-candidates":
        result = draft_candidates(repo_root)
    elif cmd == "export":
        if export_format and export_format != "csv":
            print("error: only --format csv is supported", file=sys.stderr)
            sys.exit(2)
        dest = Path(export_path) if export_path else (
            repo_root
            / ".agent"
            / "evaluations"
            / "behavior"
            / "instructions"
            / "export.csv"
        )
        path = export_instructions_csv(repo_root, dest)
        result = {"status": "exported", "path": str(path), "canonical_unchanged": True}
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (InstructionServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True, default=str))
PY
