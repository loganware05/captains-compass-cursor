# Autonomy budget — m10-external-knowledge-ti

- Plan ID: m10-external-knowledge-ti
- Issue: #74
- Branch: feature/74-m10-external-knowledge-ti
- Status: active
- Approved: 2026-08-24 (Captain)

## Limits

| Resource | Budget | Used |
|---|---:|---:|
| Agent iterations | 20 | 2 |
| Validation runs | 5 | 1 |

## Captain decisions

- Target v1.14.0
- Both knowledge ingest and HF file TI
- File export only (no live Notion MCP / HF Hub in CI)
- `fetched_at` + `refresh-ti-cache.sh --if-stale`
- Dedicated `external-knowledge-ingest` Skill (36 Skills)

## Stop conditions

- Any limit reached → Budget Stop Report under `.agent/evidence/m10-external-knowledge-ti/`
