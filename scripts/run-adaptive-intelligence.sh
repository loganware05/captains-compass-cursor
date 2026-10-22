#!/usr/bin/env bash
# run-adaptive-intelligence.sh — N3 Adaptive Intelligence scorecard (proposal-only).
#
# Requires COMPASS_ADAPTIVE_INTEL_ENABLED=1 (or --enable-gates).
# Also enables brain/assess/route gates under --enable-gates for hermetic compose.
# Never auto-applies routing/Skills/policies; never authorizes Level 3 spend.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
PHASE="compare"
ENABLE_GATES=0

usage() {
  cat <<'USAGE'
Usage:
  run-adaptive-intelligence.sh scorecard [--phase baseline|with_evidence|compare]
                                         [--repo-root PATH] [--enable-gates]

Requires COMPASS_ADAPTIVE_INTEL_ENABLED=1 (or --enable-gates).
Proposal-only scorecard; does not apply weights or approve Level 3 GPU jobs.
USAGE
}

CMD="scorecard"
if [[ $# -gt 0 && "$1" != --* ]]; then
  CMD="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root|--repo) REPO_ROOT="$2"; shift 2 ;;
    --phase) PHASE="$2"; shift 2 ;;
    --enable-gates) ENABLE_GATES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$CMD" != "scorecard" ]]; then
  echo "error: unknown command: $CMD" >&2
  usage >&2
  exit 2
fi

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_ADAPTIVE_INTEL_ENABLED=1
  export COMPASS_BRAIN_ENABLED=1
  export COMPASS_ASSESS_ENABLED=1
  export COMPASS_ROUTE_ENABLED=1
fi

export COMPASS_CONTROL_ROOT="${COMPASS_CONTROL_ROOT:-$ROOT}"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$ROOT" "$REPO_ROOT" "$PHASE" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
phase = sys.argv[3]
sys.path.insert(0, str(control_root))

from orchestrator.adaptive.enabled import adaptive_intel_enabled
from orchestrator.adaptive.service import AdaptiveServiceError, run_scorecard

if not adaptive_intel_enabled():
    print(
        "error: COMPASS_ADAPTIVE_INTEL_ENABLED is unset/off — "
        "set COMPASS_ADAPTIVE_INTEL_ENABLED=1 (or pass --enable-gates)",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    report = run_scorecard(repo_root, phase=phase, persist=True)
except (AdaptiveServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps({"status": "scorecard_complete", "report": report}, indent=2, sort_keys=True))
PY
