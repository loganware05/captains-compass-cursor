#!/usr/bin/env bash
# sync-skill-learning-ledger.sh — Minimal Linear↔learning-run linkage (M24).
# Never creates Captain approval. Fixture-safe by default.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_PATH=""
MODE="fixtures"
PROJECT_ID=""
PROJECT_NAME="NorthStar Skills Learning Loop"
PARENT_ISSUE_ID=""
MILESTONE=""
CONTROL_REV=""
PRODUCT_REV=""
DELEGATED_AGENT=""

usage() {
  cat <<'USAGE'
Usage: sync-skill-learning-ledger.sh --run PATH [options]

Options:
  --mode fixtures|link   fixtures (default) writes placeholder IDs;
                         link attaches provided Linear IDs only (no create/approve)
  --project-id ID        Linear project id
  --project-name NAME    Linear project name (default: NorthStar Skills Learning Loop)
  --parent-issue-id ID   Parent Learning Run issue (e.g. OVA-5)
  --milestone NAME       Current milestone label
  --control-revision SHA
  --product-revision SHA
  --delegated-agent ID   Optional Cursor agent id (routing candidate only)
  --repo-root PATH       Ignored alias for launcher compatibility

Does not call Linear to invent CAPTAIN_APPROVED. Does not merge PRs or install Skills.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) RUN_PATH="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --project-id) PROJECT_ID="$2"; shift 2 ;;
    --project-name) PROJECT_NAME="$2"; shift 2 ;;
    --parent-issue-id) PARENT_ISSUE_ID="$2"; shift 2 ;;
    --milestone) MILESTONE="$2"; shift 2 ;;
    --control-revision) CONTROL_REV="$2"; shift 2 ;;
    --product-revision) PRODUCT_REV="$2"; shift 2 ;;
    --delegated-agent) DELEGATED_AGENT="$2"; shift 2 ;;
    --repo-root) shift 2 ;; # accepted for northstar --repo mapping symmetry
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$RUN_PATH" ]]; then
  echo "error: --run is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$RUN_PATH" "$MODE" "$PROJECT_ID" "$PROJECT_NAME" "$PARENT_ISSUE_ID" "$MILESTONE" "$CONTROL_REV" "$PRODUCT_REV" "$DELEGATED_AGENT" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.integrations.skills_ledger import (
    SkillsLedgerError,
    sync_learning_run_ledger,
)

root = Path(sys.argv[1])
run_path = Path(sys.argv[2]).resolve()
mode = sys.argv[3]
project_id = sys.argv[4].strip() or None
project_name = sys.argv[5].strip() or None
parent_issue_id = sys.argv[6].strip() or None
milestone = sys.argv[7].strip() or None
control_revision = sys.argv[8].strip() or None
product_revision = sys.argv[9].strip() or None
delegated_agent = sys.argv[10].strip() or None

try:
    report = sync_learning_run_ledger(
        run_path,
        mode=mode,
        project_id=project_id,
        project_name=project_name,
        parent_issue_id=parent_issue_id,
        milestone=milestone,
        control_revision=control_revision,
        product_revision=product_revision,
        delegated_agent=delegated_agent,
        control_root=root,
    )
except SkillsLedgerError as exc:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(1)

print(json.dumps({"ok": True, "run_id": report.get("run_id"), "ledger": report.get("ledger")}, indent=2))
PY
