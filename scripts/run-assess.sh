#!/usr/bin/env bash
# run-assess.sh — Cognitive Core difficulty / capability-fit assessment (C3).
#
# Requires COMPASS_ASSESS_ENABLED=1. Read-oriented: never approves plans,
# promotes Skills/Policies, merges, deploys, or rewrites project memory.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
OBJECTIVE=""

usage() {
  cat <<'USAGE'
Usage:
  run-assess.sh project --objective TEXT [--repo-root PATH]

Requires COMPASS_ASSESS_ENABLED=1.
Read-oriented: never mutates authority or auto-writes canonical memory docs.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    project)
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

if [[ "$CMD" == "project" && -z "$OBJECTIVE" ]]; then
  echo "error: --objective is required for assess project" >&2
  usage >&2
  exit 2
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
# Product repos lack orchestrator/reference-profiles; fall back to control.
export COMPASS_CONTROL_ROOT="${COMPASS_CONTROL_ROOT:-$ROOT}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$OBJECTIVE" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
objective = sys.argv[4]

sys.path.insert(0, str(control_root))

from orchestrator.assess.enabled import assess_enabled
from orchestrator.assess.service import AssessServiceError, assess_project

if not assess_enabled():
    print(
        "error: COMPASS_ASSESS_ENABLED is unset/off — "
        "set COMPASS_ASSESS_ENABLED=1 to run northstar assess",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "project":
        result = assess_project(repo_root, objective)
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (AssessServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
PY
