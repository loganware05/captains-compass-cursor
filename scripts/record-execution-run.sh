#!/usr/bin/env bash
# record-execution-run.sh — Write ExecutionRun + Experience telemetry artifacts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAN_ID=""
OUTCOME="success"
OBJECTIVE=""
SKILLS=""
ISSUE=""
BRANCH=""
PR=""
SOURCE_INSTANCE="control-live"
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: record-execution-run.sh --plan-id <id> [options]

Options:
  --plan-id ID           Required plan id
  --outcome OUTCOME      success|partial|failed|cancelled|pending (default: success)
  --objective TEXT       Objective summary
  --skills LIST          Comma-separated Skill ids
  --issue REF            Issue URL or number
  --branch NAME          Branch name
  --pr URL               Pull request URL
  --source-instance NAME control-live|control-test|product-import (default: control-live)
  --repo-root PATH       Repository root (default: control repo)
  -h, --help             Show help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --outcome) OUTCOME="$2"; shift 2 ;;
    --objective) OBJECTIVE="$2"; shift 2 ;;
    --skills) SKILLS="$2"; shift 2 ;;
    --issue) ISSUE="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --pr) PR="$2"; shift 2 ;;
    --source-instance) SOURCE_INSTANCE="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$PLAN_ID" ]]; then
  echo "error: --plan-id is required" >&2
  usage >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$PLAN_ID" "$OUTCOME" "$OBJECTIVE" "$SKILLS" "$ISSUE" "$BRANCH" "$PR" "$SOURCE_INSTANCE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.telemetry.record import record_workstream

repo_root = Path(sys.argv[1]).resolve()
plan_id = sys.argv[2]
outcome = sys.argv[3]
objective = sys.argv[4]
skills_raw = sys.argv[5]
issue = sys.argv[6]
branch = sys.argv[7]
pr = sys.argv[8]
source_instance = sys.argv[9]

skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
provenance = {}
if issue:
    provenance["issue"] = issue
if branch:
    provenance["branch"] = branch
if pr:
    provenance["pull_request"] = pr

paths = record_workstream(
    repo_root,
    plan_id=plan_id,
    outcome=outcome,
    objective=objective,
    skills=skills,
    provenance=provenance,
    source_instance=source_instance,
)
print(json.dumps({k: str(v) for k, v in paths.items()}, indent=2))
PY
