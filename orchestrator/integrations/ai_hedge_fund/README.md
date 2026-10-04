# AI Hedge Fund adapter (AHF-P01)

Read-only NorthStar boundary around a **pinned**
[`virattt/ai-hedge-fund`](https://github.com/virattt/ai-hedge-fund) commit.

## Authority

- Research / paper / backtest modes only
- Never sets `approved_for_execution`
- Live broker / wallet / signing tokens are hard-denied in `policy.py`
- Default **off** via `COMPASS_AHF_ADAPTER_ENABLED`
- v1 strategy/backtest/paper surfaces are **fixture-only**

## Pin

| Field | Value |
|---|---|
| Repo | `https://github.com/virattt/ai-hedge-fund` |
| SHA | `78b779c1389e2d1452dc29606d2c4126d859b964` |
| Form | Documented SHA + optional `COMPASS_AHF_LOCAL_PATH` (recorded only; not executed in v1) |

## Enable

```bash
COMPASS_AHF_ADAPTER_ENABLED=1 \
PYTHONPATH=. python3 - <<'PY'
from orchestrator.integrations.ai_hedge_fund import get_adapter
adapter = get_adapter()
print(adapter.run_backtest()["run_id"])
PY
```

## Ops

- `create_research_run`
- `run_strategy_agents` (fixture-only)
- `get_market_state` / `get_portfolio_state`
- `run_backtest` / `run_paper_session`
- `get_decision_ledger`
- `compare_runs`

See `docs/integrations/ai-hedge-fund.md`.
