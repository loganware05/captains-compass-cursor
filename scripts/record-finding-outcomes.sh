#!/usr/bin/env bash
# record-finding-outcomes.sh — Record Code Reviewer triage outcomes (M31).
# Writes outcomes evidence + Experience lessons. Optional RoutingProposal is
# proposal-only (auto_apply=false). Never originates Captain approval.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
REPORT=""
TRIAGE=""
PLAN_ID=""
EMIT_PROPOSAL=0
NOTES=""

usage() {
  cat <<'USAGE'
Usage: record-finding-outcomes.sh --report PATH --triage PATH [options]

Options:
  --report PATH          code-review report.json (required)
  --triage PATH          triage outcomes JSON (required)
  --repo-root PATH       Repository root (default: control repo)
  --plan-id ID           Plan id recorded on Experience records
  --emit-routing-proposal  Also write a proposal-only RoutingProposal
  --notes TEXT           Notes for the RoutingProposal
  -h, --help             Show help

Triage JSON is a list of objects or {"outcomes":[...]} with:
  finding_id, decision (accepted|rejected|deferred), optional label/skill/notes
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --report) REPORT="$2"; shift 2 ;;
    --triage) TRIAGE="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --emit-routing-proposal) EMIT_PROPOSAL=1; shift ;;
    --notes) NOTES="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$REPORT" || -z "$TRIAGE" ]]; then
  echo "error: --report and --triage are required" >&2
  usage >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$REPORT" "$TRIAGE" "$PLAN_ID" "$EMIT_PROPOSAL" "$NOTES" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.review.outcomes import OutcomeError, record_finding_outcomes

repo = Path(sys.argv[1]).resolve()
report = Path(sys.argv[2]).resolve()
triage = Path(sys.argv[3]).resolve()
plan_id = sys.argv[4]
emit = sys.argv[5] == "1"
notes = sys.argv[6]

try:
    result = record_finding_outcomes(
        repo_root=repo,
        report_path=report,
        triage_path=triage,
        plan_id=plan_id,
        emit_routing_proposal=emit,
        proposal_notes=notes,
    )
except OutcomeError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

print(json.dumps(result, indent=2))
PY
