# Autonomy budget — m8-procedure-ti-cache

- Plan ID: m8-procedure-ti-cache
- Issue: #66
- Branch: feature/66-m8-procedure-ti-cache
- Status: active
- Approved: 2026-08-24 (Captain)

## Limits

| Resource | Budget | Used |
|---|---:|---:|
| Agent iterations | 20 | 0 |
| Validation runs | 5 | 2 |
| TI cache refresh batches | 5 | 0 |

## Captain decisions

- Procedure Context always render (empty when none)
- Separate `github-stars-cached` provider
- Ingest staging + approved procedure roots
- Target v1.12.0
- New `procedure-playbooks` Skill (34 Skills)

## Stop conditions

- Any limit reached → Budget Stop Report under `.agent/evidence/m8-procedure-ti-cache/`
