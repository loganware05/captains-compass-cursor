#!/usr/bin/env bash
# run-policy.sh — Policy / instruction promotion lifecycle (M50).
#
# Requires COMPASS_POLICY_PROMOTE_ENABLED=1. Never writes live .cursor/
# guidance / Skills / routing / authority. Active compose-include requires
# COMPASS_POLICY_APPLY_ENABLED=1 separately.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
EXPORT_FORMAT=""
EXPORT_PATH=""
POLICY_ID=""
INSTRUCTION_ID=""
TO_STATE=""
PROMPT_EVAL_REPORT=""
AGENT=""
SKILL_ID=""
NOTES=""
CAPTAIN_APPROVED=0

usage() {
  cat <<'USAGE'
Usage:
  run-policy.sh list [--repo-root PATH]
  run-policy.sh show --policy-id ID [--repo-root PATH]
  run-policy.sh create --instruction-id ID [--repo-root PATH]
  run-policy.sh promote --to STATE (--policy-id ID | --instruction-id ID)
                        [--prompt-eval-report ID] [--captain-approved] [--notes TEXT]
                        [--repo-root PATH]
  run-policy.sh shadow --policy-id ID [--agent NAME] [--skill-id ID] [--repo-root PATH]
  run-policy.sh materialize-proposal --policy-id ID [--repo-root PATH]
  run-policy.sh export --format csv [--out PATH] [--repo-root PATH]

Requires COMPASS_POLICY_PROMOTE_ENABLED=1.
Promotion-only / proposal-only: never auto-writes .cursor/ or grants execution.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    list|show|create|promote|shadow|materialize-proposal|export)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --policy-id)
      POLICY_ID="$2"
      shift 2
      ;;
    --instruction-id)
      INSTRUCTION_ID="$2"
      shift 2
      ;;
    --to)
      TO_STATE="$2"
      shift 2
      ;;
    --prompt-eval-report)
      PROMPT_EVAL_REPORT="$2"
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
    --notes)
      NOTES="$2"
      shift 2
      ;;
    --captain-approved)
      CAPTAIN_APPROVED=1
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
  "$POLICY_ID" "$INSTRUCTION_ID" "$TO_STATE" "$PROMPT_EVAL_REPORT" \
  "$AGENT" "$SKILL_ID" "$NOTES" "$CAPTAIN_APPROVED" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
export_format = sys.argv[4]
export_path = sys.argv[5]
policy_id = sys.argv[6]
instruction_id = sys.argv[7]
to_state = sys.argv[8]
prompt_eval_report = sys.argv[9]
agent = sys.argv[10]
skill_id = sys.argv[11]
notes = sys.argv[12]
captain_approved = sys.argv[13] == "1"

sys.path.insert(0, str(control_root))

from orchestrator.behavior.enabled import policy_promote_enabled
from orchestrator.behavior.policy.service import (
    PolicyServiceError,
    create_from_instruction,
    export_policies_csv,
    list_registry,
    materialize,
    promote,
    shadow,
    show_policy,
)

if not policy_promote_enabled():
    print(
        "error: COMPASS_POLICY_PROMOTE_ENABLED is unset/off — "
        "set COMPASS_POLICY_PROMOTE_ENABLED=1 to run northstar policy",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "list":
        result = list_registry(repo_root)
    elif cmd == "show":
        if not policy_id:
            print("error: --policy-id required", file=sys.stderr)
            sys.exit(2)
        result = show_policy(repo_root, policy_id)
    elif cmd == "create":
        if not instruction_id:
            print("error: --instruction-id required", file=sys.stderr)
            sys.exit(2)
        result = create_from_instruction(repo_root, instruction_id)
    elif cmd == "promote":
        if not to_state:
            print("error: --to STATE required", file=sys.stderr)
            sys.exit(2)
        result = promote(
            repo_root,
            to_state=to_state,
            policy_id=policy_id,
            instruction_id=instruction_id,
            prompt_eval_report_id=prompt_eval_report,
            captain_approved=captain_approved,
            notes=notes,
        )
    elif cmd == "shadow":
        if not policy_id:
            print("error: --policy-id required", file=sys.stderr)
            sys.exit(2)
        result = shadow(repo_root, policy_id, agent=agent, skill_id=skill_id)
    elif cmd == "materialize-proposal":
        if not policy_id:
            print("error: --policy-id required", file=sys.stderr)
            sys.exit(2)
        result = materialize(repo_root, policy_id)
    elif cmd == "export":
        if export_format and export_format != "csv":
            print("error: only --format csv is supported", file=sys.stderr)
            sys.exit(2)
        dest = Path(export_path) if export_path else (
            repo_root
            / ".agent"
            / "evaluations"
            / "behavior"
            / "policies"
            / "export.csv"
        )
        path = export_policies_csv(repo_root, dest)
        result = {"status": "exported", "path": str(path), "canonical_unchanged": True}
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (PolicyServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True, default=str))
PY
