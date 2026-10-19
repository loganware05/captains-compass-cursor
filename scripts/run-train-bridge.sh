#!/usr/bin/env bash
# run-train-bridge.sh — Cognitive Core Training bridge (C7).
#
# Requires COMPASS_TRAIN_BRIDGE_ENABLED=1.
# Local hermetic hand-off only — never uploads or changes live weights.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
FROM="experiences"
PLAN_ID=""
EXPORT_ID=""
EXPORT_PATH=""
OUT_DIR=""
INCLUDE_UNREVIEWED="0"
ALLOW_FIXTURES="0"
EXPORT_AUTHORIZED="0"
SECRETS_REDACTED="0"
LICENSE_REVIEWED="0"
PII_REVIEWED="0"
HANDOFF_ACK="0"
EVAL_COMPLETE="0"
SECURITY_COMPLETE="0"
CAPTAIN_APPROVAL="0"

usage() {
  cat <<'USAGE'
Usage:
  run-train-bridge.sh export --from experiences|cycles
                 [--plan-id ID] [--out PATH] [--include-unreviewed]
                 [--fixture]
                 [--export-authorized] [--secrets-redacted-ack]
                 [--license-reviewed] [--pii-reviewed]
                 [--specialized-model-handoff-ack]
                 [--repo-root PATH]
  run-train-bridge.sh review (--export-id ID | --export-path PATH)
                 [--independent-eval-complete] [--security-review-complete]
                 [--captain-approval-recorded]
                 [--repo-root PATH]

Requires COMPASS_TRAIN_BRIDGE_ENABLED=1.
Local hand-off only — never auto-uploads or changes weights.
Hermetic fixtures require --fixture or COMPASS_TRAIN_BRIDGE_FIXTURE=1.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    export|review)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --from)
      FROM="$2"
      shift 2
      ;;
    --plan-id)
      PLAN_ID="$2"
      shift 2
      ;;
    --export-id)
      EXPORT_ID="$2"
      shift 2
      ;;
    --export-path)
      EXPORT_PATH="$2"
      shift 2
      ;;
    --out)
      OUT_DIR="$2"
      shift 2
      ;;
    --include-unreviewed)
      INCLUDE_UNREVIEWED="1"
      shift
      ;;
    --fixture)
      ALLOW_FIXTURES="1"
      shift
      ;;
    --export-authorized)
      EXPORT_AUTHORIZED="1"
      shift
      ;;
    --secrets-redacted-ack)
      SECRETS_REDACTED="1"
      shift
      ;;
    --license-reviewed)
      LICENSE_REVIEWED="1"
      shift
      ;;
    --pii-reviewed)
      PII_REVIEWED="1"
      shift
      ;;
    --specialized-model-handoff-ack)
      HANDOFF_ACK="1"
      shift
      ;;
    --independent-eval-complete)
      EVAL_COMPLETE="1"
      shift
      ;;
    --security-review-complete)
      SECURITY_COMPLETE="1"
      shift
      ;;
    --captain-approval-recorded)
      CAPTAIN_APPROVAL="1"
      shift
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

if [[ "$CMD" == "review" && -z "$EXPORT_ID" && -z "$EXPORT_PATH" ]]; then
  echo "error: --export-id or --export-path is required for train review" >&2
  usage >&2
  exit 2
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$FROM" "$PLAN_ID" "$EXPORT_ID" "$EXPORT_PATH" "$OUT_DIR" \
  "$INCLUDE_UNREVIEWED" "$ALLOW_FIXTURES" \
  "$EXPORT_AUTHORIZED" "$SECRETS_REDACTED" "$LICENSE_REVIEWED" "$PII_REVIEWED" "$HANDOFF_ACK" \
  "$EVAL_COMPLETE" "$SECURITY_COMPLETE" "$CAPTAIN_APPROVAL" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
source = sys.argv[4]
plan_id = sys.argv[5] or None
export_id = sys.argv[6]
export_path = sys.argv[7] or None
out_dir = sys.argv[8] or None
include_unreviewed = sys.argv[9] == "1"
allow_fixtures = sys.argv[10] == "1"
checklist = {
    "export_authorized": sys.argv[11] == "1",
    "secrets_redacted_ack": sys.argv[12] == "1",
    "license_reviewed": sys.argv[13] == "1",
    "pii_reviewed": sys.argv[14] == "1",
    "specialized_model_handoff_ack": sys.argv[15] == "1",
}
eval_complete = sys.argv[16] == "1"
security_complete = sys.argv[17] == "1"
captain_approval = sys.argv[18] == "1"

sys.path.insert(0, str(control_root))

from orchestrator.train_bridge.enabled import train_bridge_enabled
from orchestrator.train_bridge.service import (
    TrainBridgeServiceError,
    train_export,
    train_review,
)

if not train_bridge_enabled():
    print(
        "error: COMPASS_TRAIN_BRIDGE_ENABLED is unset/off — "
        "set COMPASS_TRAIN_BRIDGE_ENABLED=1 to run northstar train",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "export":
        result = train_export(
            repo_root,
            source=source,
            plan_id=plan_id,
            checklist=checklist,
            include_unreviewed=include_unreviewed,
            allow_fixtures=allow_fixtures,
            out_dir=Path(out_dir) if out_dir else None,
        )
    elif cmd == "review":
        result = train_review(
            repo_root,
            export_id=export_id,
            export_file=Path(export_path) if export_path else None,
            independent_eval_complete=eval_complete,
            security_review_complete=security_complete,
            captain_approval_recorded=captain_approval,
        )
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (TrainBridgeServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
PY
