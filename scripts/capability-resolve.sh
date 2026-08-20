#!/usr/bin/env bash
# capability-resolve.sh — Resolve required capabilities and rank Skills for an objective
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OBJECTIVE="${1:-}"
if [[ -z "$OBJECTIVE" ]]; then
  echo "usage: capability-resolve.sh \"<objective text>\"" >&2
  exit 1
fi

PYTHONPATH="$ROOT" python3 - "$ROOT" "$OBJECTIVE" <<'PY'
import json, sys
from orchestrator.resolver.resolve import resolve_to_dict

repo_root = sys.argv[1]
objective = sys.argv[2]
print(json.dumps(resolve_to_dict(repo_root, objective), indent=2))
PY
