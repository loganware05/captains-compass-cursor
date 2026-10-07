#!/usr/bin/env bash
# AHF-P05 portfolio experimentation demo (research / paper / observe-only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export COMPASS_AHF_ADAPTER_ENABLED="${COMPASS_AHF_ADAPTER_ENABLED:-1}"
export COMPASS_AHF_EXPERIMENT_ENABLED="${COMPASS_AHF_EXPERIMENT_ENABLED:-1}"
export COMPASS_DECISION_PROVIDER="${COMPASS_DECISION_PROVIDER:-file}"
export COMPASS_DECISION_AHF_SHADOW="${COMPASS_DECISION_AHF_SHADOW:-1}"
export PYTHONPATH="${PYTHONPATH:-.}"

python3 - <<'PY'
from pathlib import Path
from orchestrator.integrations.ai_hedge_fund import run_portfolio_experiment

report = run_portfolio_experiment(
    Path("."),
    objective="BTC paper allocation experiment",
    run_paper_if_accepted=True,
)
acc = report["acceptance"]
print(
    "experiment",
    report["experiment_id"],
    "winner",
    acc.get("winner_arm"),
    "passed",
    acc.get("passed"),
)
print("evidence", report.get("evidence_path"))
print("paper", bool(report.get("paper_session")), "blocked", report.get("paper_blocked_reason"))
print("approved_for_execution", report.get("approved_for_execution"))
ranking = acc.get("comparison", {}).get("ranking_by_return_then_sharpe")
print("ranking", ranking)
PY
