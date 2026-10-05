#!/usr/bin/env bash
# Captain-facing demo: On-Chain Analyst + optional AHF/Jev shadow (AHF-P04).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-}:."
export COMPASS_AHF_ADAPTER_ENABLED="${COMPASS_AHF_ADAPTER_ENABLED:-1}"
# Shadow optional — default file provider when enabled by Captain.
# export COMPASS_DECISION_AHF_SHADOW=1
# export COMPASS_DECISION_PROVIDER=file

python3 - <<'PY'
from pathlib import Path
from orchestrator.integrations.ai_hedge_fund import get_adapter, maybe_run_ahf_signal_shadow
from orchestrator.integrations.ai_hedge_fund.onchain_analyst import (
    OnChainAnalyst,
    compose_with_ahf,
    write_analysis_evidence,
)

root = Path(".")
analysis = OnChainAnalyst().analyze()
print("analysis", analysis.signal, analysis.confidence, analysis.netflow_btc)
research = get_adapter(enabled=True).create_research_run(
    objective="BTC paper allocation — on-chain composed"
)
shadow = maybe_run_ahf_signal_shadow(
    root, asset="BTC", state=analysis.to_jev_state(), adapter_manifest=research
)
composed = compose_with_ahf(analysis, research_manifest=research, jev_shadow_ref=shadow)
ref = write_analysis_evidence(root, analysis, composed=composed)
print("evidence", ref["evidence_path"])
print("approved_for_execution", composed["approved_for_execution"])
PY
