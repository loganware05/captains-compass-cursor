# Autonomy Budget Ledger

## Metadata

- Plan ID: m22-m23-northstar-ops-ti-flywheel
- Budget file: m22-northstar-unattended-ops
- Issue: local/m22-northstar-unattended-ops
- Branch: cursor/m22-northstar-unattended-ops-6044
- Created: 2026-09-09
- Last updated: 2026-09-09
- Status: ACTIVE

## Limits (from approved plan)

- Maximum iterations: 8
- Maximum failed validation cycles: 3
- Live credential usage in CI: 0 (doubles/fixtures only)
- Weight-apply / live Skill apply without Captain flag: 0
- Stop on scope change: true
- Stop on destructive operation: true
- Stop on unresolved security high: true

## Usage

- Iterations used: 1
- Failed validation cycles: 0
- Estimated cost used (USD): 0
- Cost is estimate: true
- Elapsed minutes: 0
- Weight-apply operations used: 0

## Cycle log

| Date | Iteration | Result | Notes |
|---|---|---|---|
| 2026-09-09 | iteration 1 | in_progress | M22 implementation start after Captain approval |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/m22-northstar-unattended-ops/BUDGET_STOP_REPORT.md`.
