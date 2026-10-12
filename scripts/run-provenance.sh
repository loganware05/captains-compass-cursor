#!/usr/bin/env bash
# run-provenance.sh — Execution provenance + behavior exemplars (M53).
#
# Requires COMPASS_PROVENANCE_ENABLED=1. Proposal/read-only: never promotes
# Skills/Policies or grants approved_for_execution.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
EXPORT_FORMAT=""
EXPORT_PATH=""
EXECUTION_ID=""
PROVENANCE_ID=""
EXEMPLAR_ID=""
EVALUATION_ID=""
POLARITY=""
SUMMARY=""
SURFACE="provenance"

usage() {
  cat <<'USAGE'
Usage:
  run-provenance.sh capture --execution-id ID [--repo-root PATH]
  run-provenance.sh list [--repo-root PATH]
  run-provenance.sh show --provenance-id ID [--repo-root PATH]
  run-provenance.sh export --format csv [--out PATH] [--repo-root PATH]
  run-provenance.sh examples-list [--polarity positive|negative] [--repo-root PATH]
  run-provenance.sh examples-show --exemplar-id ID [--repo-root PATH]
  run-provenance.sh examples-draft --polarity POLARITY [--evaluation-id ID]
                                   [--provenance-id ID] [--execution-id ID]
                                   [--summary TEXT] [--repo-root PATH]
  run-provenance.sh examples-export --format csv [--out PATH] [--repo-root PATH]

Requires COMPASS_PROVENANCE_ENABLED=1.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    capture|list|show|export|examples-list|examples-show|examples-draft|examples-export)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --execution-id)
      EXECUTION_ID="$2"
      shift 2
      ;;
    --provenance-id)
      PROVENANCE_ID="$2"
      shift 2
      ;;
    --exemplar-id)
      EXEMPLAR_ID="$2"
      shift 2
      ;;
    --evaluation-id)
      EVALUATION_ID="$2"
      shift 2
      ;;
    --polarity)
      POLARITY="$2"
      shift 2
      ;;
    --summary)
      SUMMARY="$2"
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
  "$EXECUTION_ID" "$PROVENANCE_ID" "$EXEMPLAR_ID" "$EVALUATION_ID" \
  "$POLARITY" "$SUMMARY" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
export_format = sys.argv[4]
export_path = sys.argv[5]
execution_id = sys.argv[6]
provenance_id = sys.argv[7]
exemplar_id = sys.argv[8]
evaluation_id = sys.argv[9]
polarity = sys.argv[10]
summary = sys.argv[11]

sys.path.insert(0, str(control_root))

from orchestrator.behavior.enabled import provenance_enabled
from orchestrator.behavior.exemplars.service import (
    ExemplarServiceError,
    draft_exemplar,
    export_exemplars_csv,
    list_exemplars,
    load_exemplar,
)
from orchestrator.behavior.provenance.service import (
    ProvenanceServiceError,
    capture_from_execution,
    export_provenance_csv,
    list_provenance,
    load_provenance,
)

if not provenance_enabled():
    print(
        "error: COMPASS_PROVENANCE_ENABLED is unset/off — "
        "set COMPASS_PROVENANCE_ENABLED=1 to run northstar provenance/examples",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "capture":
        if not execution_id:
            print("error: --execution-id required", file=sys.stderr)
            sys.exit(2)
        result = capture_from_execution(repo_root, execution_id)
    elif cmd == "list":
        result = list_provenance(repo_root)
    elif cmd == "show":
        if not provenance_id:
            print("error: --provenance-id required", file=sys.stderr)
            sys.exit(2)
        result = load_provenance(repo_root, provenance_id)
    elif cmd == "export":
        if export_format and export_format != "csv":
            print("error: only --format csv is supported", file=sys.stderr)
            sys.exit(2)
        dest = Path(export_path) if export_path else (
            repo_root / ".agent" / "evaluations" / "behavior" / "provenance" / "export.csv"
        )
        path = export_provenance_csv(repo_root, dest)
        result = {"status": "exported", "path": str(path)}
    elif cmd == "examples-list":
        result = list_exemplars(repo_root, polarity=polarity)
    elif cmd == "examples-show":
        if not exemplar_id:
            print("error: --exemplar-id required", file=sys.stderr)
            sys.exit(2)
        result = load_exemplar(repo_root, exemplar_id)
    elif cmd == "examples-draft":
        if not polarity:
            print("error: --polarity required", file=sys.stderr)
            sys.exit(2)
        result = draft_exemplar(
            repo_root,
            polarity=polarity,
            evaluation_id=evaluation_id,
            provenance_id=provenance_id,
            execution_id=execution_id,
            summary=summary,
        )
    elif cmd == "examples-export":
        if export_format and export_format != "csv":
            print("error: only --format csv is supported", file=sys.stderr)
            sys.exit(2)
        dest = Path(export_path) if export_path else (
            repo_root / ".agent" / "examples" / "export.csv"
        )
        path = export_exemplars_csv(repo_root, dest)
        result = {"status": "exported", "path": str(path), "auto_promoted": False}
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (ProvenanceServiceError, ExemplarServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True, default=str))
PY
