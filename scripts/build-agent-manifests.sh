#!/usr/bin/env bash
# build-agent-manifests.sh — Build proposed agent manifests for an objective
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OBJECTIVE="${1:-}"
PLAN_ID="${2:-draft}"

if [[ -z "$OBJECTIVE" ]]; then
  echo "usage: build-agent-manifests.sh \"<objective text>\" [plan-id]" >&2
  exit 1
fi

PYTHONPATH="$ROOT" python3 - "$ROOT" "$OBJECTIVE" "$PLAN_ID" <<'PY'
import json, sys
from orchestrator.assembler.manifest import build_manifests_for_objective

repo_root = sys.argv[1]
objective = sys.argv[2]
plan_id = sys.argv[3]
print(json.dumps(build_manifests_for_objective(repo_root, objective, plan_id=plan_id), indent=2))
PY
