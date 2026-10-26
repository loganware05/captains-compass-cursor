#!/usr/bin/env bash
# run-n5-feedback.sh — N5 Skill-fit / routing feedback from N4 deltas.
#
# Requires COMPASS_N5_FEEDBACK_ENABLED=1 (or --enable-gates).
# Proposal-only: never applies matcher weights or promotes policies.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
N4_REPORT=""
WRITE_PROPOSALS=1
ENABLE_GATES=0

usage() {
  cat <<'USAGE'
Usage:
  run-n5-feedback.sh [--n4-report PATH] [--repo-root PATH]
                     [--no-write-proposals] [--enable-gates]

Requires COMPASS_N5_FEEDBACK_ENABLED=1 (or --enable-gates).
Default N4 input: .agent/evidence/n4-cross-stack-benchmark/LATEST_hermetic.json
Writes proposal-only RoutingProposal under .agent/routing/proposals/ unless
--no-write-proposals. Never calls apply-routing-proposal.sh.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root|--repo) REPO_ROOT="$2"; shift 2 ;;
    --n4-report) N4_REPORT="$2"; shift 2 ;;
    --no-write-proposals) WRITE_PROPOSALS=0; shift ;;
    --enable-gates) ENABLE_GATES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_N5_FEEDBACK_ENABLED=1
fi

export COMPASS_CONTROL_ROOT="${COMPASS_CONTROL_ROOT:-$ROOT}"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$ROOT" "$REPO_ROOT" "$N4_REPORT" "$WRITE_PROPOSALS" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
n4_raw = sys.argv[3]
write_proposals = sys.argv[4] == "1"
sys.path.insert(0, str(control_root))

from orchestrator.feedback.n5.enabled import n5_enabled
from orchestrator.feedback.n5.service import N5ServiceError, run_n5_feedback

if not n5_enabled():
    print(
        "error: COMPASS_N5_FEEDBACK_ENABLED is unset/off — "
        "set COMPASS_N5_FEEDBACK_ENABLED=1 (or pass --enable-gates)",
        file=sys.stderr,
    )
    sys.exit(2)

n4_path = Path(n4_raw) if n4_raw else None
try:
    report = run_n5_feedback(
        repo_root,
        n4_report=n4_path,
        write_proposals=write_proposals,
        persist=True,
    )
except (N5ServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps({"status": "n5_complete", "report": report}, indent=2, sort_keys=True))
PY
