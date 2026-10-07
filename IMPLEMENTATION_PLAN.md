# Implementation Plan — AHF-P05 / Portfolio Experimentation Program

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `ahf-p05-portfolio-experiment` |
| Approved | 2026-10-07 — Captain: analyze Technical development plan work + live Jev; proceed with AHF-P05 |
| Linear | OVA-66 (create if missing) · Project P-OVA-5 |
| Prerequisite | AHF-P01–P04 on `main` (v1.52.0 @ `c23eb51`) |
| Product | NorthStar control repo |
| Baseline | **v1.52.0** @ `c23eb51` |
| Proposed release | **v1.53.0** |
| Rollback | `rollback/pre-ahf-p05-portfolio-experiment` @ `c23eb51` |
| Branch | `cursor/ahf-p05-portfolio-experiment-8613` |

## Analysis (Captain utilization + Technical development plan + live Jev)

### What the Captain already validated (steps 0–4)

Captain confirmed local runs of the utilization runbook with a **live TypeSafe Jev key**:

| Step | System | Outcome implied |
|---|---|---|
| 0 | Doctor / pull / secrets | Control ≥ v1.52.0 + BTC P03 available |
| 1 | AHF-P03 exchange netflow | Collector + signal engine path exercised |
| 2 | AHF-P04 OnChainAnalyst | Deterministic signal + evidence refs |
| 3 | AHF-P01 adapter | Research / backtest / paper fixture ops |
| 4 | AHF-P02 Jev shadow | `COMPASS_DECISION_PROVIDER=jev` + `COMPASS_DECISION_AHF_SHADOW=1` |

### Technical development plan agent (Cursor IDE)

The more technical script execution was performed in a **local Cursor IDE agent** (“Technical development plan”). This cloud run’s environment only lists `bitcoin-data-collector` agents and does **not** include that IDE transcript. Analysis therefore treats the Captain’s successful live-Jev runbook exercise as the ground truth for operability, and uses the Notion Phase-5 contract as the product definition for AHF-P05.

### Live Jev features — what they prove vs what they don’t

**Proven / operable today**

- DecisionProvider `jev` path for `suggest_ahf_strategies` / `triage_ahf_signal` (pinned `jev-1.13.0`)
- Shadow evidence contract (`applied: false`, fail-closed on error)
- Composition: OnChainAnalyst → `to_jev_state()` → signal shadow
- File fixtures remain CI-hermetic default; live key stays Captain-local

**Still missing for Phase 5 (AHF-P05)**

- Multi-arm portfolio experiment program (baseline vs on-chain vs Jev+on-chain)
- Structured investment + orchestration metric comparison across arms
- Deterministic acceptance criteria before any paper-session arm
- Evidence folder + Captain-facing demo for the experiment lifecycle
- No silent promotion / authority mutation (unchanged hard rule)

### Verdict → AHF-P05 scope

Ship a **fixture-backed portfolio experimentation harness** that reuses the existing adapter, OnChainAnalyst, and Jev shadow surfaces. Live Jev remains optional (Captain-local) behind existing env gates; CI stays hermetic via `file` provider.

## Desired Outcome

```
run_portfolio_experiment(repo_root)
  → arm A: baseline backtest (no on-chain)
  → arm B: on-chain analyst + backtest
  → arm C: on-chain + optional Jev strategy/signal shadow + backtest
  → multi-arm metric comparison
  → acceptance gate (deterministic)
  → optional paper session only if accepted
  → evidence under .agent/evidence/ahf-p05-portfolio-experiment/
  → always approved_for_execution: false
```

## Acceptance Criteria

- [x] `orchestrator/integrations/ai_hedge_fund/experiment.py` with 3 arms + acceptance
- [x] Hermetic arm fixtures + unit tests
- [x] Env gate `COMPASS_AHF_EXPERIMENT_ENABLED` (default off)
- [x] Demo `scripts/ahf-portfolio-experiment.sh`
- [x] Runbook section + docs/ADR/VERSION **1.53.0**
- [x] Paper path blocked unless acceptance passes

## Non-Goals

- Live broker / real capital
- Executing local `ai-hedge-fund` checkout (still fixture-only)
- M50 Policy promotion
- New DecisionProvider backtest-triage question pack (deferred)
- AHF-P06 behavioral ledger coupling (later)

## Approval Record

Captain Logan Ware — 2026-10-07 — proceed with AHF-P05 after live Jev steps 0–4 + Technical development plan agent script runs.
