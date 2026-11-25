#!/usr/bin/env bash
# start-repair-loop.sh — B4 FIND→PROVE→packet→FIX→TEST→SUBMIT prepare.
# Never auto-merges. Verified findings only. Captain-gated FIX.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
REPORT=""
FINDING=""
RUN_ID=""
ALLOWLIST="$ROOT/templates/agent/review/github-allowlist.yml"
SEVERITY_FLOOR="medium"
CAPTAIN_FIX=0
OPEN_DRAFT=0
REPOSITORY=""
AGENT_ID=""

usage() {
  cat <<'USAGE'
Usage: start-repair-loop.sh --report PATH --finding ID [options]

Options:
  --report PATH              code-review report.json (required)
  --finding ID               verified finding id (required)
  --repo-root PATH           evidence root (default: control repo)
  --repository owner/name    override report repository (fixtures)
  --allowlist PATH           github-allowlist.yml (default: template)
  --severity-floor LEVEL     default medium
  --run-id ID                evidence run id
  --selected-agent-id ID     optional router selection to record
  --captain-authorized-fix mark FIX authorized → hermetic FIX/TEST + submit_prepared
  --open-draft-pr            request draft-PR helper (requires captain auth; execute
                             only if COMPASS_REPAIR_EXECUTE_DRAFT_PR=1)
  -h, --help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --report) REPORT="$2"; shift 2 ;;
    --finding) FINDING="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --repository) REPOSITORY="$2"; shift 2 ;;
    --allowlist) ALLOWLIST="$2"; shift 2 ;;
    --severity-floor) SEVERITY_FLOOR="$2"; shift 2 ;;
    --run-id) RUN_ID="$2"; shift 2 ;;
    --selected-agent-id) AGENT_ID="$2"; shift 2 ;;
    --captain-authorized-fix) CAPTAIN_FIX=1; shift ;;
    --open-draft-pr) OPEN_DRAFT=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$REPORT" || -z "$FINDING" ]]; then
  echo "error: --report and --finding are required" >&2
  usage >&2
  exit 2
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$REPORT" "$FINDING" "$RUN_ID" "$ALLOWLIST" "$SEVERITY_FLOOR" "$CAPTAIN_FIX" "$REPOSITORY" "$AGENT_ID" "$OPEN_DRAFT" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.repair.loop import RepairError, start_repair

repo = Path(sys.argv[1]).resolve()
report = Path(sys.argv[2])
finding = sys.argv[3]
run_id = sys.argv[4] or None
allowlist = Path(sys.argv[5]) if sys.argv[5] else None
floor = sys.argv[6]
captain = sys.argv[7] == "1"
repository = sys.argv[8] or None
agent = sys.argv[9] or None
open_draft = sys.argv[10] == "1"

try:
    result = start_repair(
        repo_root=repo,
        report_path=report,
        finding_id=finding,
        run_id=run_id,
        allowlist_path=allowlist,
        severity_floor=floor,
        captain_authorized_fix=captain,
        open_draft_pr=open_draft,
        selected_agent_id=agent,
        repository_override=repository,
    )
except RepairError as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
    raise SystemExit(1)

print(
    json.dumps(
        {
            "ok": True,
            "run_id": result["run_id"],
            "stage": result["stage"],
            "submit_prepared": bool((result.get("submit") or {}).get("prepared")),
            "auto_merge": False,
            "evidence": f".agent/evidence/repair/{result['run_id']}/",
        },
        indent=2,
    )
)
PY
