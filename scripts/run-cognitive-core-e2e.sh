#!/usr/bin/env bash
# run-cognitive-core-e2e.sh — Hermetic (or sandbox) C1–C7 Cognitive Core evaluation.
#
# Requires COMPASS_BRAIN_ENABLED, COMPASS_ASSESS_ENABLED, COMPASS_CYCLE_ENABLED,
# COMPASS_ROUTE_ENABLED, COMPASS_REA_ENABLED, and COMPASS_TRAIN_BRIDGE_ENABLED
# (or pass --enable-gates to export them for this process only).
#
# Never grants authority, uploads training data, or promotes model weights.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
MODE="hermetic"
OBJECTIVE=""
ENABLE_GATES=0
EVIDENCE_DIR=""
WRITE_EVIDENCE=1

usage() {
  cat <<'USAGE'
Usage:
  run-cognitive-core-e2e.sh [--repo-root PATH] [--mode hermetic|sandbox]
                            [--objective TEXT] [--enable-gates]
                            [--evidence-dir PATH] [--no-write-evidence]

Requires Cognitive Core feature gates (or --enable-gates):
  COMPASS_BRAIN_ENABLED=1
  COMPASS_ASSESS_ENABLED=1
  COMPASS_CYCLE_ENABLED=1
  COMPASS_ROUTE_ENABLED=1
  COMPASS_REA_ENABLED=1
  COMPASS_TRAIN_BRIDGE_ENABLED=1

Writes a schema-validated report under
  .agent/evidence/e2e-cognitive-core-evaluation/
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root|--repo)
      REPO_ROOT="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --objective)
      OBJECTIVE="$2"
      shift 2
      ;;
    --enable-gates)
      ENABLE_GATES=1
      shift
      ;;
    --evidence-dir)
      EVIDENCE_DIR="$2"
      shift 2
      ;;
    --no-write-evidence)
      WRITE_EVIDENCE=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_BRAIN_ENABLED=1
  export COMPASS_ASSESS_ENABLED=1
  export COMPASS_CYCLE_ENABLED=1
  export COMPASS_ROUTE_ENABLED=1
  export COMPASS_REA_ENABLED=1
  export COMPASS_TRAIN_BRIDGE_ENABLED=1
  export COMPASS_TRAIN_BRIDGE_FIXTURE=1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$MODE" "$OBJECTIVE" "$EVIDENCE_DIR" "$WRITE_EVIDENCE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.e2e.enabled import missing_gates, require_e2e_gates
from orchestrator.e2e.service import E2EServiceError, run_cognitive_core_e2e

_root, repo, mode, objective, evidence_dir, write_flag = sys.argv[1:7]
try:
    require_e2e_gates()
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

kwargs = {
    "mode": mode,
    "write_evidence": write_flag == "1",
}
if objective.strip():
    kwargs["objective"] = objective
if evidence_dir.strip():
    kwargs["evidence_dir"] = Path(evidence_dir)

try:
    report = run_cognitive_core_e2e(Path(repo), **kwargs)
except (E2EServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(report, indent=2, sort_keys=True))
status = report.get("overall_status")
# warn-only thresholds: exit 0 for pass/warn, 1 for fail
sys.exit(0 if status in {"pass", "warn"} else 1)
PY
