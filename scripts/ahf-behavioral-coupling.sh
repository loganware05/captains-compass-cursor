#!/usr/bin/env bash
# AHF-P06 — couple AHF-P05 experiment → behavior loop + readiness verdict.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

EXPERIMENT_PATH="${1:-}"
if [[ -z "$EXPERIMENT_PATH" ]]; then
  # Prefer Captain local evidence if present; else fixture sample
  CANDIDATE=".agent/evidence/ahf-p05-portfolio-experiment/exp-20261007T211148Z-23fa367a/experiment.json"
  if [[ -f "$CANDIDATE" ]]; then
    EXPERIMENT_PATH="$CANDIDATE"
  else
    EXPERIMENT_PATH="orchestrator/integrations/ai_hedge_fund/fixtures/experiment_outcome_sample.json"
  fi
fi

export COMPASS_AHF_BEHAVIOR_COUPLING_ENABLED="${COMPASS_AHF_BEHAVIOR_COUPLING_ENABLED:-1}"
export COMPASS_BEHAVIOR_EVAL_ENABLED="${COMPASS_BEHAVIOR_EVAL_ENABLED:-0}"
export COMPASS_BEHAVIOR_LEARN_ENABLED="${COMPASS_BEHAVIOR_LEARN_ENABLED:-0}"
export COMPASS_DECISION_PROVIDER="${COMPASS_DECISION_PROVIDER:-file}"
export PYTHONPATH="${PYTHONPATH:-.}"

python3 - "$EXPERIMENT_PATH" <<'PY'
import sys
from pathlib import Path
from orchestrator.integrations.ai_hedge_fund import run_behavioral_coupling

path = Path(sys.argv[1])
captain_live = "exp-20261007T211148Z-23fa367a" in str(path)
bundle = run_behavioral_coupling(
    Path("."),
    path,
    run_evaluate=True,
    run_learn=False,
    captain_reported_live_jev=True,  # Captain reported live Jev for this milestone
)
r = bundle["readiness"]
print("experiment", path)
print("recommend_approved_for_execution", r.get("recommend_approved_for_execution"))
print("approved_for_execution", r.get("approved_for_execution"))
print("confidence_band", r.get("confidence_band"))
print("failed_gates", r.get("failed_gates"))
print("readiness_evidence", bundle.get("readiness_evidence_path"))
print("coupling_evidence", bundle.get("coupling_evidence_path"))
print("rationale", r.get("rationale"))
PY
