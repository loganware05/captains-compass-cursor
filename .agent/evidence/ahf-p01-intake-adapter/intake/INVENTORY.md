# AHF-P01 Intake — virattt/ai-hedge-fund

| Field | Value |
|---|---|
| Date | 2026-10-04 |
| Plan | `ahf-p01-intake-adapter` |
| Linear | OVA-62 · P-OVA-5 |
| Upstream | https://github.com/virattt/ai-hedge-fund |
| Pinned SHA | `78b779c1389e2d1452dc29606d2c4126d859b964` |
| Default branch observed | `main` |
| Description | An AI Hedge Fund Team — educational AI-powered hedge fund proof of concept |
| Pin form | Documented SHA + optional `COMPASS_AHF_LOCAL_PATH` (Captain decision) |
| Execution in v1 | Fixture-only NorthStar adapter — no live broker, no local subprocess invoke |

## Executable surfaces (inventory summary)

Observed from public repository positioning and NorthStar adapter contract (not a full clone SBOM dump in CI):

- Multi-agent investor / strategy analysis
- Paper trading sessions
- Historical backtesting
- Portfolio / market state inspection
- Decision / session ledger style persistence

External data dependency (upstream): Financial Datasets style market APIs — **never** committed; Captain-local only if a future plan enables local invoke.

## Supply-chain / SBOM notes

- Treat upstream as an **external candidate**, not an installed Skill.
- Do not vendor the full tree into NorthStar in P01.
- Before any future local-invoke plan: run dependency/SBOM review Skill on the pinned commit checkout.
- Secrets (API keys) must not enter fixtures, prompts, or git.

## NorthStar mapping

| Upstream concept | NorthStar seam |
|---|---|
| Research / agents | `create_research_run`, `run_strategy_agents` (fixture) |
| Backtest | `run_backtest` |
| Paper trade | `run_paper_session` |
| Portfolio / market | `get_portfolio_state`, `get_market_state` |
| Ledger | `get_decision_ledger` |
| Compare | `compare_runs` |

## Not in P01

- Live trading
- Jev question packs (AHF-P02)
- BTC on-chain features (AHF-P03 in `bitcoin-data-collector`)
