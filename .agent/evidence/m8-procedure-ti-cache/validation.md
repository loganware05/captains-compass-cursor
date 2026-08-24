# M8 validation evidence — m8-procedure-ti-cache

- Date: 2026-08-24
- Branch: `feature/66-m8-procedure-ti-cache`
- Issue: #66

## Commands

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_*.py' -v
./tests/run.sh
./tests/evals/run.sh
```

## Results

| Check | Result |
|---|---|
| Doctor | 0 errors, 0 warnings |
| Orchestrator unit tests | 132 passed |
| tests/run.sh | 114 passed |
| tests/evals/run.sh | 39 passed |

## Captain decisions verified

- Procedure Context always render (empty when none)
- Separate `github-stars-cached` provider
- Ingest staging + approved procedure roots
- New `procedure-playbooks` Skill (34 Skills)
