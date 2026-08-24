# Autonomy budget — m8-procedure-ti-cache

- Plan ID: m8-procedure-ti-cache
- Issue: #66
- Branch: feature/66-m8-procedure-ti-cache (merged #67)
- Status: **COMPLETE**
- Approved: 2026-08-24 (Captain)
- Completed: 2026-08-24

## Limits

| Resource | Budget | Used |
|---|---:|---:|
| Agent iterations | 20 | 3 |
| Validation runs | 5 | 3 |
| TI cache refresh batches | 5 | 0 |

## Captain decisions

- Procedure Context always render (empty when none)
- Separate `github-stars-cached` provider
- Ingest staging + approved procedure roots
- Target v1.12.0
- New `procedure-playbooks` Skill (34 Skills)

## Cycle log

| Date | Iteration | Result | Notes |
|---|---|---|---|
| 2026-08-24 | 0 | approved | Captain decisions locked; issue #66, rollback, branch |
| 2026-08-24 | 1 | pass | M8 impl; doctor + 132 unit + 39 evals + tests/run 114 |
| 2026-08-24 | 2 | pass | Feature PR #67 merged |
| 2026-08-24 | 3 | complete | T-F release prep v1.12.0 |

## Stop conditions

- Any limit reached → Budget Stop Report under `.agent/evidence/m8-procedure-ti-cache/`
