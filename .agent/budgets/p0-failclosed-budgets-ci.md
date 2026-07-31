# Autonomy Budget Ledger

## Metadata

- Plan ID: p0-failclosed-budgets-ci
- Issue: #26
- Branch: feature/26-p0-failclosed-budgets-ci
- Created: 2026-07-30
- Last updated: 2026-07-30
- Status: COMPLETE

## Limits (from approved plan)

- Maximum iterations: 8
- Maximum failed validation cycles: 3
- Maximum estimated cost (USD): moderate
- Maximum elapsed minutes: 240
- Stop on scope change: true
- Stop on destructive operation: true
- Stop on unresolved security high: true

## Usage

- Iterations used: 2
- Failed validation cycles: 0
- Estimated cost used (USD): 0
- Cost is estimate: true
- Elapsed minutes: ~90

## Cycle log

| 2026-07-30 | iteration 1 | pass | Implemented P0; PR #27; CI green |
| 2026-07-30 | iteration 2 | pass | Tagged v1.2.0; sandbox refresh PR #8; P1 plan drafted |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/<slug>/BUDGET_STOP_REPORT.md`.
