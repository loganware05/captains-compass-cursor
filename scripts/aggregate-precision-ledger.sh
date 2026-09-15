#!/usr/bin/env bash
# aggregate-precision-ledger.sh — Aggregate finding outcomes into a precision ledger (M33 / B5).
# Writes ledger + dashboard evidence. Optional RoutingProposal is proposal-only
# (auto_apply=false). Never originates Captain approval.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
OUTCOMES=""
OUTCOMES_DIR=""
PLAN_ID="b5-precision-ledger"
LEDGER_ID=""
MIN_SAMPLE="5"
EMIT_PROPOSAL=0
WRITE_EXPERIENCE=1
NOTES=""

usage() {
  cat <<'USAGE'
Usage: aggregate-precision-ledger.sh (--outcomes PATH | --outcomes-dir PATH) [options]

Options:
  --outcomes PATH              Single outcomes.json bundle (M31)
  --outcomes-dir PATH          Scan recursively for outcomes.json
  --repo-root PATH             Repository root (default: control repo)
  --plan-id ID                 Plan id on ledger / Experience (default: b5-precision-ledger)
  --ledger-id ID               Stable ledger id (default: generated)
  --min-sample N               Min decided findings before priority proposal (default: 5)
  --emit-priority-proposal     Write proposal-only RoutingProposal when sample allows
  --skip-experience            Do not write an Experience lesson
  --notes TEXT                 Notes for the RoutingProposal
  -h, --help                   Show help

Precision = accepted / (accepted + rejected). Deferred is counted but excluded
from the denominator. Proposals never auto-apply.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --outcomes) OUTCOMES="$2"; shift 2 ;;
    --outcomes-dir) OUTCOMES_DIR="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --ledger-id) LEDGER_ID="$2"; shift 2 ;;
    --min-sample) MIN_SAMPLE="$2"; shift 2 ;;
    --emit-priority-proposal) EMIT_PROPOSAL=1; shift ;;
    --skip-experience) WRITE_EXPERIENCE=0; shift ;;
    --notes) NOTES="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$OUTCOMES" && -z "$OUTCOMES_DIR" ]]; then
  echo "error: --outcomes or --outcomes-dir is required" >&2
  usage >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - \
  "$REPO_ROOT" \
  "$OUTCOMES" \
  "$OUTCOMES_DIR" \
  "$PLAN_ID" \
  "$LEDGER_ID" \
  "$MIN_SAMPLE" \
  "$EMIT_PROPOSAL" \
  "$WRITE_EXPERIENCE" \
  "$NOTES" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.review.precision import PrecisionError, aggregate_precision

repo = Path(sys.argv[1]).resolve()
outcomes = Path(sys.argv[2]).resolve() if sys.argv[2] else None
outcomes_dir = Path(sys.argv[3]).resolve() if sys.argv[3] else None
plan_id = sys.argv[4]
ledger_id = sys.argv[5] or None
min_sample = int(sys.argv[6])
emit = sys.argv[7] == "1"
write_exp = sys.argv[8] == "1"
notes = sys.argv[9]

try:
    result = aggregate_precision(
        repo_root=repo,
        outcomes=outcomes,
        outcomes_dir=outcomes_dir,
        plan_id=plan_id,
        ledger_id=ledger_id,
        min_sample_for_proposal=min_sample,
        write_experience_lesson=write_exp,
        emit_priority_proposal=emit,
        proposal_notes=notes,
    )
except PrecisionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

print(json.dumps(result, indent=2))
PY
