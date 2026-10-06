# Implementation Plan — AHF-P04 / On-Chain Analyst + Captain Runbook

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `ahf-p04-onchain-analyst` |
| Approved | 2026-10-05 — Captain: proceed with next steps after P02/P03 merges |
| Linear | [OVA-65](https://linear.app/ovaltechnologysolutions/issue/OVA-65/ahf-p04-on-chain-analyst-capability-captain-utilization-runbook) · P-OVA-5 |
| Prerequisite | AHF-P01–P03 on `main` / base (v1.51.0 + BTC #11) |
| Product | NorthStar control repo (+ runbook covering BTC collector) |
| Baseline | **v1.51.0** @ `b809c75` |
| Proposed release | **v1.52.0** |
| Rollback | `rollback/pre-ahf-p04-onchain-analyst` @ `b809c75` |
| Branch | `cursor/ahf-p04-onchain-analyst-runbook-8613` |

## Request

1. Ship an **On-Chain Analyst** module that consumes normalized on-chain features
   (AHF-P03 schema), emits evidence-referenced signals, and composes with the
   AHF adapter + Jev shadow triage.
2. Ship a **Captain utilization runbook** so the foundation is operable without
   further agent guidance.

## Desired Outcome

```
Normalized on-chain state (fixture or BTC snapshot excerpt)
  → OnChainAnalyst.analyze() → signal + evidence refs + confidence
  → optional maybe_run_ahf_signal_shadow (Jev)
  → optional AHF research_run composition note
  → evidence under .agent/evidence/ahf-p04-onchain-analyst/
+ docs/integrations/ahf-captain-runbook.md (+ Notion mirror)
```

## Acceptance Criteria

- [x] `orchestrator/integrations/ai_hedge_fund/onchain_analyst.py`
- [x] Hermetic fixtures + unit tests
- [x] Compose helper linking analyst → AHF adapter / Jev shadow (observe-only)
- [x] Captain runbook with step-by-step utilization
- [x] Docs, ADR, VERSION 1.52.0, Notion mirror

## Non-Goals

- Live trading / Glassnode key in CI
- AHF-P05 full portfolio experimentation program
- Mutating Skill registry or Policy activation

## Approval Record

Captain Logan Ware — 2026-10-05 — proceed with next steps + utilization instructions.
