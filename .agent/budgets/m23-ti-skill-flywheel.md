# Autonomy Budget Ledger

## Metadata

- Plan ID: m22-m23-northstar-ops-ti-flywheel
- Budget file: m23-ti-skill-flywheel
- Issue: local/m23-ti-skill-flywheel
- Branch: cursor/m23-ti-skill-flywheel-6044
- Created: 2026-09-10
- Last updated: 2026-09-10
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

- Iterations used: 2
- Failed validation cycles: 0
- Estimated cost used (USD): 0
- Cost is estimate: true
- Elapsed minutes: 120
- Weight-apply operations used: 0

## Cycle log

| Date | Iteration | Result | Notes |
|---|---|---|---|
| 2026-09-10 | iteration 1 | in_progress | M23 implementation after Captain directed start |
| 2026-09-10 | iteration 2 | pass | doctor + tests/run.sh 121/121; draft_gates moved to promotion |

## Stop condition

When any usage field meets or exceeds its limit, stop immediately and write a
Budget Stop Report under `.agent/evidence/m23-ti-skill-flywheel/BUDGET_STOP_REPORT.md`.
