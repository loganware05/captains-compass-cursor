# Autonomy Budget Ledger

## Metadata

- Plan ID: m1-capability-aware-planning
- Issue: #35
- Branch: feature/35-m1-capability-aware-planning
- Created: 2026-08-19
- Last updated: 2026-08-19
- Status: COMPLETE

## Limits (from approved plan)

- Maximum iterations: 25
- Maximum failed validation cycles: 5
- Maximum estimated cost (USD): Captain-defined
- Maximum elapsed minutes: 7200
- Stop on scope change: true
- Stop on destructive operation: true
- Stop on unresolved security high: true

## Usage

- Iterations used: 9
- Failed validation cycles: 0
- Estimated cost used (USD): 0
- Cost is estimate: true
- Elapsed minutes: 0

## Cycle log

| Date | Iteration | Result | Notes |
|---|---|---|---|
| 2026-08-19 | 1 | in progress | Phase A schemas + orchestrator skeleton |
| 2026-08-19 | 2–8 | pass | Phases B–H + tests |
| 2026-08-19 | 9 | pass | Release prep VERSION 1.5.0 |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/m1-capability-aware-planning/BUDGET_STOP_REPORT.md`.
