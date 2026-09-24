# Autonomy Budget Ledger

## Metadata

- Plan ID: m41-jev-decision-service
- Issue: Local placeholder (gh read-only; ADR-004)
- Branch: cursor/m41-jev-decision-service-753c
- Created: 2026-09-24
- Last updated: 2026-09-24 (validation)
- Status: ACTIVE

## Limits (from approved plan)

- Maximum iterations: 8
- Maximum failed validation cycles: 3
- Maximum estimated cost (USD): Captain-set before live Jev (fixtures free)
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

<!-- One line per cycle: date | iteration N | result | notes -->

| 2026-09-24 | iteration 0 | start | Captain approved; WS0 folded in; pin jev-1.13.0 |
| 2026-09-24 | iteration 1 | pass | Implemented DecisionProvider+WS0; adversarial fixes; suite 125/evals 43 |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/<slug>/BUDGET_STOP_REPORT.md`.
