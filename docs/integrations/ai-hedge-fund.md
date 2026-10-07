# AI Hedge Fund adapter (AHF-P01 / v1.50.0)

Canonical package: `orchestrator/integrations/ai_hedge_fund/`  
Plan: `ahf-p01-intake-adapter` · Linear [OVA-62](https://linear.app/ovaltechnologysolutions/issue/OVA-62/ahf-p01-ai-hedge-fund-intake-read-only-northstar-adapter) · Project [NorthStar On-Chain / AI Hedge Fund](https://linear.app/ovaltechnologysolutions/project/northstar-on-chain-ai-hedge-fund-67b1475ea115)

Pinned upstream: [`virattt/ai-hedge-fund`](https://github.com/virattt/ai-hedge-fund) @ `78b779c1389e2d1452dc29606d2c4126d859b964`

## Authority

- Decision/adapter outputs never set `approved_for_execution`
- Modes: `research` | `paper` | `backtest` only
- Live / broker / wallet / signing tokens → `LiveExecutionDenied`
- Default / CI: adapter **disabled** (`COMPASS_AHF_ADAPTER_ENABLED` unset)
- v1 surfaces are **fixture-only** (no local AHF subprocess execution)

## Env contract

| Variable | Default | Meaning |
|---|---|---|
| `COMPASS_AHF_ADAPTER_ENABLED` | unset/off | Must be `1`/`true`/`yes`/`on` to use adapter |
| `COMPASS_AHF_LOCAL_PATH` | unset | Optional local checkout path recorded on manifests only (not executed in v1) |
| `COMPASS_AHF_EXPERIMENT_ENABLED` | unset/off | Must be on to run AHF-P05 portfolio experiment harness |

## Operations

```python
from orchestrator.integrations.ai_hedge_fund import get_adapter

adapter = get_adapter(enabled=True)
adapter.create_research_run(objective="…")
adapter.run_strategy_agents()          # fixture-only
adapter.get_market_state()
adapter.get_portfolio_state()
adapter.run_backtest()
adapter.run_paper_session()
adapter.get_decision_ledger()
adapter.compare_runs(left, right)

# AHF-P05 multi-arm experiment
from orchestrator.integrations.ai_hedge_fund import run_portfolio_experiment
run_portfolio_experiment(Path("."), run_paper_if_accepted=True)
```

## Technology Intelligence

Offline fixture:
`orchestrator/providers/technology_intelligence/fixtures/stars-ai-hedge-fund.json`

```bash
COMPASS_TI_PROVIDER=file ./scripts/capability-plan.sh --plan-id ahf-demo \
  "paper portfolio backtesting research"
```

Candidate remains `approved_for_execution: false`.

## Related next plans

- ~~**AHF-P02** — Jev shadow~~ shipped v1.51.0
- ~~**AHF-P03** — BTC exchange netflow~~ shipped in `bitcoin-data-collector` #11
- ~~**AHF-P04** — On-Chain Analyst + Captain runbook~~ see
  `docs/integrations/ahf-captain-runbook.md` (v1.52.0)
- ~~**AHF-P05** — portfolio experimentation~~ shipped v1.53.0 (`experiment.py`, `COMPASS_AHF_EXPERIMENT_ENABLED`)
- **AHF-P06+** — behavioral ledger coupling (deferred)

## Evidence

- Intake notes: `.agent/evidence/ahf-p01-intake-adapter/intake/`
- Tests: `tests/orchestrator/test_ahf_adapter.py`
