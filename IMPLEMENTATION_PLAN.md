# Implementation Plan — AHF-P02 / Jev Shadow over AHF Adapter

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `ahf-p02-jev-shadow` |
| Approved | 2026-10-05 — Captain: "proceed with AHF-P02 (Jev shadow), then AHF-P03" |
| Linear | [OVA-63](https://linear.app/ovaltechnologysolutions/issue/OVA-63/ahf-p02-jev-shadow-decisions-over-ahf-adapter) · [P-OVA-5](https://linear.app/ovaltechnologysolutions/project/northstar-on-chain-ai-hedge-fund-67b1475ea115) |
| Prerequisite | AHF-P01 merged (#188) → **v1.50.0** @ `d771e6e` |
| Product | NorthStar control repo `captains-compass-cursor` |
| Baseline | **v1.50.0** @ `d771e6e` |
| Proposed release | **v1.51.0** |
| Rollback | `rollback/pre-ahf-p02-jev-shadow` @ `d771e6e` |
| Branch | `cursor/ahf-p02-jev-shadow-8613` |

## Request

Add observe-only Jev DecisionProvider surfaces for AHF strategy/agent selection
and signal triage beside the AHF-P01 fixture adapter. Shadow evidence only —
never mutates adapter results or grants execution.

## Desired Outcome

```
AHF adapter run (fixture)
  → compact redacted state
  → DecisionProvider suggest_ahf_strategies / triage_ahf_signal
  → shadow evidence under .agent/evidence/ahf-p02-jev-shadow/
  → adapter outputs unchanged (applied: false)
```

## Decision Summary

| Principle | Implication |
|---|---|
| Shadow only | No apply path in P02 |
| Reuse DecisionProvider | Extend stub/file/jev; pin `jev-1.13.0` |
| Hermetic CI | File fixtures; live Jev Captain-local via existing env |
| Fail closed | API/fixture miss → abstain; baseline adapter path continues |
| Authority | Never `approved_for_execution`; never live trading |

## Acceptance Criteria

- [x] Types + Protocol methods for AHF strategy selection and signal triage
- [x] Question packs `ahf_strategy_select_v1`, `ahf_signal_triage_v1`
- [x] File fixtures + hermetic tests
- [x] `COMPASS_DECISION_AHF_SHADOW` gate (default off)
- [x] Evidence writer under `.agent/evidence/ahf-p02-jev-shadow/`
- [x] Docs + ADR + VERSION 1.51.0
- [x] Live Jev path wired but optional (key via env; not required for CI)

## Non-Goals

- Ranking apply / mutating adapter agent lists
- AHF-P03 BTC on-chain (separate repo/plan)
- Live trading

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain Logan Ware |
| Approved at | 2026-10-05 |
| Method | Explicit: proceed with AHF-P02 then AHF-P03 |
| Note | TypeSafe Jev API key available Captain-local; not committed |
