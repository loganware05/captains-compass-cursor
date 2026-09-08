#!/usr/bin/env bash
# reconcile-northstar-run.sh — Reconcile a persisted NorthStar run
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: reconcile-northstar-run.sh --run <path-to-run.json>

Reloads a persisted NorthStar run and reconciles fixture connectors.
GitHub remains the engineering authority on conflict.
USAGE
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) RUN="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$RUN" ]]; then
  usage
  exit 1
fi

PYTHONPATH="$ROOT" python3 - "$RUN" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.integrations.routine import reconcile_northstar_run

result = reconcile_northstar_run(Path(sys.argv[1]))
print(json.dumps(result, indent=2))
PY
