#!/usr/bin/env bash
# propose-context-selection.sh — Build proposal-only context slice tuning from Experiences (M17).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPERIENCES=""
REPO_ROOT="$ROOT"
NOTES=""

usage() {
  cat <<'USAGE'
Usage: propose-context-selection.sh --experiences <file1.json[,file2.json...]> [--repo-root PATH]

Writes a context-selection proposal with auto_apply=false. Does not mutate active profile.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --experiences) EXPERIENCES="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$EXPERIENCES" ]]; then
  echo "error: --experiences is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$EXPERIENCES" "$NOTES" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.planning.context_selection import (
    build_context_selection_proposal,
    write_context_selection_proposal,
)
from orchestrator.routing.propose import load_experiences

repo = Path(sys.argv[1]).resolve()
paths = [Path(p.strip()).resolve() for p in sys.argv[2].split(",") if p.strip()]
notes = sys.argv[3]
experiences = load_experiences(paths)
proposal = build_context_selection_proposal(experiences, notes=notes)
path = write_context_selection_proposal(repo, proposal)
print(json.dumps({"proposal": str(path), "auto_apply": False}, indent=2))
PY
