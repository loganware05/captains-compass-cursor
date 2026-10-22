#!/usr/bin/env bash
# run-status.sh — Project Overseer status surface (M51).
#
# Requires COMPASS_STATUS_ENABLED=1. Read-oriented: never approves plans,
# promotes Skills/Policies, merges, deploys, or rewrites project memory.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
EXPORT_FORMAT=""
EXPORT_PATH=""
SINCE=""
SNAPSHOT_ID=""
LEDGER_PATH=""

usage() {
  cat <<'USAGE'
Usage:
  run-status.sh snapshot [--repo-root PATH]
  run-status.sh explain [--snapshot-id ID] [--repo-root PATH]
  run-status.sh compare --since SHA [--repo-root PATH]
  run-status.sh reconcile [--snapshot-id ID] [--repo-root PATH]
  run-status.sh closeout [--snapshot-id ID] [--ledger PATH] [--repo-root PATH]
  run-status.sh export --format csv [--out PATH] [--repo-root PATH]

Requires COMPASS_STATUS_ENABLED=1.
Read-oriented / proposal-only: never mutates authority, auto-writes memory docs,
or auto-closes GitHub issues.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    snapshot|explain|compare|reconcile|closeout|export)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --since)
      SINCE="$2"
      shift 2
      ;;
    --snapshot-id)
      SNAPSHOT_ID="$2"
      shift 2
      ;;
    --ledger)
      LEDGER_PATH="$2"
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
  "$SINCE" "$SNAPSHOT_ID" "$LEDGER_PATH" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
export_format = sys.argv[4]
export_path = sys.argv[5]
since = sys.argv[6]
snapshot_id = sys.argv[7]
ledger_path = sys.argv[8]

sys.path.insert(0, str(control_root))

from orchestrator.status.enabled import status_enabled
from orchestrator.status.service import (
    StatusServiceError,
    closeout,
    compare,
    explain,
    export_csv,
    reconcile,
    snapshot,
)

if not status_enabled():
    print(
        "error: COMPASS_STATUS_ENABLED is unset/off — "
        "set COMPASS_STATUS_ENABLED=1 to run northstar status",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "snapshot":
        result = snapshot(repo_root)
    elif cmd == "explain":
        result = explain(repo_root, snapshot_id=snapshot_id)
    elif cmd == "compare":
        if not since:
            print("error: --since SHA required", file=sys.stderr)
            sys.exit(2)
        result = compare(repo_root, since=since)
    elif cmd == "reconcile":
        result = reconcile(repo_root, snapshot_id=snapshot_id)
    elif cmd == "closeout":
        result = closeout(
            repo_root, snapshot_id=snapshot_id, ledger_path=ledger_path
        )
    elif cmd == "export":
        if export_format and export_format != "csv":
            print("error: only --format csv is supported", file=sys.stderr)
            sys.exit(2)
        dest = Path(export_path) if export_path else (
            repo_root / ".agent" / "status" / "export.csv"
        )
        path = export_csv(repo_root, dest)
        result = {"status": "exported", "path": str(path), "canonical_unchanged": True}
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (StatusServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True, default=str))
PY
