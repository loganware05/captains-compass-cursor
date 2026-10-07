# Captain Utilization Runbook — NorthStar × Jev × AHF × BTC On-Chain

Linear: [OVA-65](https://linear.app/ovaltechnologysolutions/issue/OVA-65/ahf-p04-on-chain-analyst-capability-captain-utilization-runbook) · Project [NorthStar On-Chain / AI Hedge Fund](https://linear.app/ovaltechnologysolutions/project/northstar-on-chain-ai-hedge-fund-67b1475ea115)

**Authority reminder:** Everything below is research / paper / observe-only.
Nothing here authorizes live trading, broker access, or `approved_for_execution`.

---

## What you have (foundation)

| Layer | Repo | What it does | Gate |
|---|---|---|---|
| **AHF-P01** Adapter | `captains-compass-cursor` | Fixture-backed paper/backtest/research ops + TI candidate | `COMPASS_AHF_ADAPTER_ENABLED=1` |
| **AHF-P02** Jev shadow | control repo | Strategy selection + signal triage (observe-only) | `COMPASS_DECISION_AHF_SHADOW=1` |
| **AHF-P03** Exchange netflow | `bitcoin-data-collector` | Fills inflow/outflow/netflow on snapshots | `COMPASS_EXCHANGE_FLOW_PROVIDER=file` or Glassnode key |
| **AHF-P04** On-Chain Analyst | control repo | Normalized features → evidence-referenced signal | Always available (deterministic) |
| **AHF-P05** Portfolio experiment | control repo | Baseline vs on-chain vs Jev+on-chain compare + acceptance | `COMPASS_AHF_EXPERIMENT_ENABLED=1` |
| **AHF-P06** Behavior coupling | control repo | Experiment → telemetry/evaluate + readiness deny-by-default | `COMPASS_AHF_BEHAVIOR_COUPLING_ENABLED=1` |

Pinned AHF upstream: `virattt/ai-hedge-fund` @ `78b779c1389e2d1452dc29606d2c4126d859b964`

---

## Step-by-step: Captain daily / weekly use

### 0. One-time setup

1. Pull latest:
   - Control: `git pull` on `captains-compass-cursor` `main` (need **≥ v1.54.0** for P06; **v1.53.0** has P01–P05).
   - BTC: `git pull` on `bitcoin-data-collector` base branch (includes P03).
2. Optional secrets (Captain machine only — **never commit**):
   - TypeSafe Jev: `COMPASS_JEV_API_KEY` or `TYPESAFE_API_KEY`
   - Glassnode (live flows): `GLASSNODE_API_KEY`
3. Confirm doctor (control repo): `./scripts/doctor.sh`

### 1. Run BTC market intel with exchange netflow (AHF-P03)

From `bitcoin-data-collector`:

```bash
# Hermetic / demo (no paid API)
export COMPASS_EXCHANGE_FLOW_PROVIDER=file
python btc_market_intel_collector.py --output-dir outputs

# Or live Glassnode (Captain-local key)
export GLASSNODE_API_KEY='…'          # do not paste into chat / git
export COMPASS_EXCHANGE_FLOW_PROVIDER=glassnode
python btc_market_intel_collector.py --output-dir outputs
```

Check the snapshot JSON for:

- `on_chain_data.exchange_inflow_btc` / `exchange_outflow_btc` / `exchange_netflow_btc`
- provenance: `exchange_flow_provider`, `exchange_flow_freshness_seconds`, `coverage`

Rule signal:

```bash
python signal_engine.py outputs/btc_market_intel_<timestamp>.json --pretty
```

### 2. Analyze on-chain features in NorthStar (AHF-P04)

From `captains-compass-cursor`:

```bash
# Default fixture
PYTHONPATH=. python3 - <<'PY'
from orchestrator.integrations.ai_hedge_fund.onchain_analyst import OnChainAnalyst, write_analysis_evidence
from pathlib import Path
a = OnChainAnalyst().analyze()
print(a.signal, a.confidence, a.drivers)
print(write_analysis_evidence(Path('.'), a))
PY

# Or point at a real BTC snapshot
PYTHONPATH=. python3 - <<'PY'
from pathlib import Path
from orchestrator.integrations.ai_hedge_fund.onchain_analyst import OnChainAnalyst, write_analysis_evidence
snap = Path('/path/to/btc_market_intel_….json')  # from step 1
a = OnChainAnalyst().analyze(snap)
print(a.to_dict())
print(write_analysis_evidence(Path('.'), a))
PY
```

Or the demo script:

```bash
chmod +x scripts/ahf-onchain-demo.sh
./scripts/ahf-onchain-demo.sh
```

### 3. Paper research via AHF adapter (AHF-P01)

```bash
export COMPASS_AHF_ADAPTER_ENABLED=1
PYTHONPATH=. python3 - <<'PY'
from orchestrator.integrations.ai_hedge_fund import get_adapter
a = get_adapter()
print(a.create_research_run(objective='BTC paper allocation')['run_id'])
print(a.run_backtest()['results']['metrics'])
print(a.run_paper_session()['results']['pnl'])
PY
```

Optional: record a local checkout path for provenance only (not executed in v1):

```bash
export COMPASS_AHF_LOCAL_PATH=/path/to/ai-hedge-fund
```

### 4. Shadow Jev decisions (AHF-P02) — file or live

**Hermetic (recommended first):**

```bash
export COMPASS_DECISION_PROVIDER=file
export COMPASS_DECISION_AHF_SHADOW=1
export COMPASS_AHF_ADAPTER_ENABLED=1
PYTHONPATH=. python3 - <<'PY'
from pathlib import Path
from orchestrator.integrations.ai_hedge_fund import (
    get_adapter, maybe_run_ahf_strategy_shadow, maybe_run_ahf_signal_shadow,
)
from orchestrator.integrations.ai_hedge_fund.onchain_analyst import OnChainAnalyst
root = Path('.')
run = get_adapter(enabled=True).create_research_run(objective='BTC paper allocation')
print(maybe_run_ahf_strategy_shadow(root, objective='BTC paper allocation', adapter_manifest=run))
analysis = OnChainAnalyst().analyze()
print(maybe_run_ahf_signal_shadow(root, asset='BTC', state=analysis.to_jev_state()))
PY
```

**Live Jev (Captain-local):**

```bash
export COMPASS_DECISION_PROVIDER=jev
export COMPASS_JEV_MODEL_ID=jev-1.13.0
export COMPASS_JEV_API_KEY='…'   # or TYPESAFE_API_KEY — never commit
export COMPASS_DECISION_AHF_SHADOW=1
# then same Python as above
```

Evidence lands under `.agent/evidence/ahf-p02-jev-shadow/` and
`.agent/evidence/ahf-p04-onchain-analyst/`. Always `applied: false`.

### 5. Compose the loop (recommended weekly ritual)

1. Collect BTC snapshot with exchange flows (step 1).
2. Run On-Chain Analyst on that snapshot (step 2).
3. Open an AHF research/backtest run (step 3).
4. Optionally enable Jev shadow for strategy + signal (step 4).
5. Run AHF-P05 portfolio experiment (step 7) and review acceptance.
6. Review evidence folders — **do not** treat high confidence as trade authority.
7. If a change to routing/instructions is desired, feed outcomes into NorthStar
   behavioral loop (`northstar evaluate` / `learn` / `prompt-eval`) as
   **proposal-only** — still requires Captain approval for authority changes.

### 6. Technology Intelligence (discover, don’t execute)

```bash
COMPASS_TI_PROVIDER=file ./scripts/capability-plan.sh --plan-id ahf-demo \
  "paper portfolio backtesting research"
```

`virattt/ai-hedge-fund` appears as a candidate with
`approved_for_execution: false`.

---

## Safety checklist (every session)

- [ ] No live broker / wallet / signing in any env var or request mode
- [ ] API keys only in shell env or local `.env` (gitignored)
- [ ] Shadow flags off in CI / default installs
- [ ] Evidence reviewed before any proposed promotion
- [ ] Captain plan approval before product behavior changes

---

## 7. Portfolio experimentation (AHF-P05)

Hermetic (CI / first run):

```bash
export COMPASS_AHF_ADAPTER_ENABLED=1
export COMPASS_AHF_EXPERIMENT_ENABLED=1
export COMPASS_DECISION_PROVIDER=file
export COMPASS_DECISION_AHF_SHADOW=1
./scripts/ahf-portfolio-experiment.sh
```

Live Jev (Captain-local — same as step 4):

```bash
export COMPASS_DECISION_PROVIDER=jev
export COMPASS_JEV_MODEL_ID=jev-1.13.0
export COMPASS_JEV_API_KEY='…'   # never commit
export COMPASS_AHF_ADAPTER_ENABLED=1
export COMPASS_AHF_EXPERIMENT_ENABLED=1
export COMPASS_DECISION_AHF_SHADOW=1
./scripts/ahf-portfolio-experiment.sh
```

Inspect `.agent/evidence/ahf-p05-portfolio-experiment/<id>/experiment.json`:

- `arms.baseline` / `onchain` / `jev_onchain` metrics
- `acceptance.passed` / `winner_arm` / checks
- `paper_session` only when acceptance passes
- Always `approved_for_execution: false`

## 8. Behavioral coupling + execution readiness (AHF-P06)

```bash
export COMPASS_AHF_BEHAVIOR_COUPLING_ENABLED=1
# Optional: also enable M46 evaluate
# export COMPASS_BEHAVIOR_EVAL_ENABLED=1
# export COMPASS_DECISION_PROVIDER=file   # or jev
./scripts/ahf-behavioral-coupling.sh \
  .agent/evidence/ahf-p05-portfolio-experiment/exp-20261007T211148Z-23fa367a/experiment.json
```

Readiness evidence lands under `.agent/evidence/ahf-p06-behavioral-coupling/`.
Expect `recommend_approved_for_execution: false` until non-fixture backtests,
sustained paper results, live risk controls, security review, and Captain
written approval all exist.

## What comes next (AHF-P07+)

Deferred / gated:

- Deeper on-chain families (whale cohorts, stablecoin supply, etc.)
- Optional Jev backtest-triage question pack
- Any live-execution program — only after readiness gates flip and Captain
  writes explicit approval (confidence alone is never enough)

Track: [NorthStar On-Chain / AI Hedge Fund](https://linear.app/ovaltechnologysolutions/project/northstar-on-chain-ai-hedge-fund-67b1475ea115)
