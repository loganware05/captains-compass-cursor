# Autonomy Budget Ledger

## Metadata

- Plan ID: `audit-p0-governance-hygiene`
- Issue: #280
- Branch: `feature/280-audit-p0-governance-hygiene`
- Created: 2026-11-21
- Last updated: 2026-11-21
- Status: ACTIVE

## Limits (from approved plan)

- Maximum iterations: 12
- Maximum failed validation cycles: 3
- Maximum estimated cost (USD): default
- Maximum elapsed minutes: 240
- Stop on scope change: true
- Stop on destructive operation: true
- Stop on unresolved security high: true

## Usage

- Iterations used: 1
- Failed validation cycles: 0
- Estimated cost used (USD): 0
- Cost is estimate: true
- Elapsed minutes: ~40

## Cycle log

| Timestamp | Event | Iterations | Notes |
|---|---|---:|---|
| 2026-11-21 | Approved + provisioned | 0 | Issue #280, worktree, rollback tag |
| 2026-11-21 | Impl cycle 1 | 1 | Finding 001 + test isolation + docs; targeted tests OK |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/audit-p0-governance-hygiene/BUDGET_STOP_REPORT.md`.
