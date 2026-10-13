#!/usr/bin/env bash
# run-brain.sh — Cognitive Core project-state surface (C1).
#
# Requires COMPASS_BRAIN_ENABLED=1. Read-oriented: never approves plans,
# promotes Skills/Policies, merges, deploys, or rewrites project memory.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
SNAPSHOT_ID=""

usage() {
  cat <<'USAGE'
Usage:
  run-brain.sh sync [--repo-root PATH]
  run-brain.sh status [--repo-root PATH]
  run-brain.sh show --snapshot-id ID [--repo-root PATH]

Requires COMPASS_BRAIN_ENABLED=1.
Read-oriented: never mutates authority or auto-writes canonical memory docs.
Persists under .agent/project-state/ only.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    sync|status|show)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --snapshot-id)
      SNAPSHOT_ID="$2"
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
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$SNAPSHOT_ID" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
snapshot_id = sys.argv[4]

sys.path.insert(0, str(control_root))

from orchestrator.cognitive.enabled import brain_enabled
from orchestrator.cognitive.service import BrainServiceError, show, status, sync

if not brain_enabled():
    print(
        "error: COMPASS_BRAIN_ENABLED is unset/off — "
        "set COMPASS_BRAIN_ENABLED=1 to run northstar brain",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "sync":
        result = sync(repo_root)
    elif cmd == "status":
        result = status(repo_root)
    elif cmd == "show":
        result = show(repo_root, snapshot_id=snapshot_id)
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (BrainServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
PY
