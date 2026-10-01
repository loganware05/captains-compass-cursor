# Autonomy Budget Ledger

## Metadata

- Plan ID: m48-instruction-registry
- Issue: OVA-60
- Branch: cursor/m48-instruction-registry-plan-3192
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

| 2026-10-01 | iteration 0 | start | Captain approved; rollback/pre-m48-instruction-registry @ 402573e |
| 2026-10-01 | iteration 1 | implement | registry under behavior, PICCO compose, draft-from-candidates, evaluate hash wire, v1.48.0 |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/m48-instruction-registry/BUDGET_STOP_REPORT.md`.
