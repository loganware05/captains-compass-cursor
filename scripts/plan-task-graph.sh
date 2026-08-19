#!/usr/bin/env bash
# plan-task-graph.sh — Build a validated task graph for an objective
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OBJECTIVE="${1:-}"
if [[ -z "$OBJECTIVE" ]]; then
  echo "usage: plan-task-graph.sh \"<objective text>\"" >&2
  exit 1
fi

PYTHONPATH="$ROOT" python3 - "$ROOT" "$OBJECTIVE" <<'PY'
import json, sys
from orchestrator.planner.build import build_task_graph

repo_root = sys.argv[1]
objective = sys.argv[2]
print(json.dumps(build_task_graph(objective), indent=2))
PY
