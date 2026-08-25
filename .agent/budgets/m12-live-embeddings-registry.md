# Autonomy Budget Ledger

## Metadata

- Plan ID: m12-live-embeddings-registry
- Issue: #82
- Branch: feature/82-m12-live-embeddings-registry
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

- Iterations used: 0
- Failed validation cycles: 0
- Estimated cost used (USD): 0
- Cost is estimate: true
- Elapsed minutes: 0

## Cycle log

| Date | Iteration | Result | Notes |
|---|---:|---|---|
| 2026-08-24 | 0 | approved | Kickoff: issue #82, rollback, branch, decisions locked |
| 2026-08-24 | 1 | pass | T-A–T-D impl; doctor + 153 unit + 40 evals + tests/run 114 |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/m12-live-embeddings-registry/BUDGET_STOP_REPORT.md`.
