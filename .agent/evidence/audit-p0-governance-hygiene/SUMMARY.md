# Evidence — audit-p0-governance-hygiene (#280)

## Changes

1. **Finding 001 fixed** — `ensure_policy_for_instruction()` always creates `candidate`.
2. **Test isolation** — N3 scorecard persists to temp evidence; specialized dry-run adapters under `.agent/tmp-specialized-dry-run/`.
3. **Governance closeout** — #247 closed; #278 kept open; PROGRESS/CHANGELOG/DECISIONS/ADR-110 amended; VERSION **1.87.1**.

## Validation

| Check | Result |
|---|---|
| Targeted Finding 001 / N3 / specialized tests | pass |
| Formal `KnownGapTests` (bypass_observed=False) | pass |
| `unittest discover` orchestrator | see `unittest-orchestrator.txt` |
| `./scripts/doctor.sh` | 0 errors, 1 warning (skill inode carry-over — P1 backlog) |
| Tracked fixture hygiene after tests | clean |

## Rollback

`git checkout rollback/pre-audit-p0-governance-hygiene` / tag @ `38d3563`
