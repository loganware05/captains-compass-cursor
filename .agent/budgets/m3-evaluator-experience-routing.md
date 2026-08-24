# Autonomy Budget Ledger

## Metadata

- Plan ID: m3-evaluator-experience-routing
- Issue: #45
- Branch: feature/45-m3-evaluator-experience-routing
- Created: 2026-08-24
- Last updated: 2026-08-24
- Status: ACTIVE

## Limits (from approved plan)

- Maximum iterations: 20
- Maximum failed validation cycles: 5
- Maximum estimated cost (USD): Captain-defined
- Maximum elapsed minutes: 7200
- Stop on scope change: true
- Stop on destructive operation: true
- Stop on unresolved security high: true

## Usage

- Iterations used: 2
- Failed validation cycles: 0
- Estimated cost used (USD): 0
- Cost is estimate: true
- Elapsed minutes: ~120

## Cycle log

| Date | Iteration | Result | Notes |
|---|---|---|---|
| 2026-08-24 | 0 | approved | Kickoff: issue #45, rollback, branch |
| 2026-08-24 | 1 | impl | T-A–T-F evaluator, routing, promotion, proficiency |
| 2026-08-24 | 2 | pass | doctor + 84 unit + 38 evals + tests/run 114 |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/m3-evaluator-experience-routing/BUDGET_STOP_REPORT.md`.
