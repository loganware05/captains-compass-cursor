# Autonomy Budget Ledger

## Metadata

- Plan ID: m47-behavior-pattern-learning
- Issue: OVA-59
- Branch: cursor/m47-behavior-pattern-learning-plan-3192
- Created: 2026-10-01
- Last updated: 2026-10-01
- Status: ACTIVE

## Limits (from approved plan)

- Maximum iterations: 12
- Maximum failed validation cycles: 3
- Maximum estimated cost (USD): Captain-set (fixtures free)
- Maximum elapsed minutes: stop after 3 failed validation cycles
- Stop on scope change: true
- Stop on destructive operation: true
- Stop on unresolved security high: true

## Usage

- Iterations used: 1
- Failed validation cycles: 0
- Estimated cost used (USD): 0
- Cost is estimate: true
- Elapsed minutes: 0

## Cycle log

| 2026-10-01 | iteration 0 | start | Captain approved; rollback/pre-m47-behavior-pattern-learning @ cb4f463 |
| 2026-10-01 | iteration 1 | implement | schemas, detector, store, northstar learn, tests, docs v1.47.0 |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/m47-behavior-pattern-learning/BUDGET_STOP_REPORT.md`.
