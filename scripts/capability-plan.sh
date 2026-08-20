#!/usr/bin/env bash
# capability-plan.sh — Build capability-aware planning artifacts and render plan sections
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: capability-plan.sh [--plan-id ID] [--sections-only] "<objective>"

Builds resolve.json, task-graph.json, manifests.json under .agent/plans/<plan-id>/
and prints IMPLEMENTATION_PLAN.md capability sections to stdout.

Options:
  --plan-id ID       Plan identifier (default: draft)
  --sections-only    Print markdown sections only (default)
  --json             Print summary JSON instead of markdown
  -h, --help         Show help
USAGE
}

PLAN_ID="draft"
MODE="sections"
OBJECTIVE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plan-id)
      PLAN_ID="${2:-}"
      shift 2
      ;;
    --sections-only)
      MODE="sections"
      shift
      ;;
    --json)
      MODE="json"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      OBJECTIVE="$1"
      shift
      ;;
  esac
done

if [[ -z "$OBJECTIVE" ]]; then
  echo "error: objective text is required" >&2
  usage >&2
  exit 1
fi

PYTHONPATH="$ROOT" python3 - "$ROOT" "$OBJECTIVE" "$PLAN_ID" "$MODE" <<'PY'
import json, sys
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections

repo_root, objective, plan_id, mode = sys.argv[1:5]
artifacts = build_capability_plan(repo_root, objective, plan_id=plan_id)
if mode == "json":
    print(json.dumps({
        "plan_id": artifacts.plan_id,
        "objective": artifacts.objective,
        "artifact_paths": artifacts.artifact_paths,
        "capability_gaps": artifacts.resolve.get("capability_gaps", []),
        "recommended_skill_ids": artifacts.resolve.get("recommended_skill_ids", []),
        "task_count": len(artifacts.task_graph.get("tasks", [])),
        "manifest_count": len(artifacts.manifests.get("manifests", [])),
    }, indent=2))
else:
    print(render_capability_plan_sections(artifacts))
PY
