# Precision dashboard — `b5-fixture-demo`

Created: 2026-09-15T20:46:41Z
Plan: `b5-precision-ledger`
Min sample for proposal: 5

| Skill / specialist | Kind | Accepted | Rejected | Deferred | Decided | Precision |
|---|---|---:|---:|---:|---:|---:|
| code-reviewer | skill | 0 | 1 | 1 | 1 | 0.0% |
| security-review | specialist | 4 | 1 | 0 | 5 | 80.0% |

## Locks

- `captain_approval=false` (ledger never originates Captain approval)
- `auto_apply=false` / `captain_approved=false` (no silent reputation mutation)
- Deferred findings are excluded from the precision denominator
