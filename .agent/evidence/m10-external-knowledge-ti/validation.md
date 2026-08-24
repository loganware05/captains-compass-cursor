# M10 validation evidence — m10-external-knowledge-ti

- Date: 2026-08-24
- Branch: `feature/74-m10-external-knowledge-ti`
- Issue: #74

## Commands

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_*.py'
./tests/run.sh
./tests/evals/run.sh
```

## Results

| Check | Result |
|---|---|
| Doctor | 0 errors, 0 warnings |
| Orchestrator unit tests | 142 passed |
| tests/run.sh | 114 passed |
| tests/evals/run.sh | 39 passed |

## Captain decisions verified

- Target v1.14.0
- Both knowledge ingest and HF file TI
- File export only
- `fetched_at` + `refresh-ti-cache.sh --if-stale`
- Dedicated `external-knowledge-ingest` Skill (36 Skills)
