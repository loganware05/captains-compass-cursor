# M7 validation evidence — m7-performance-ti

- Date: 2026-08-24
- Branch: `feature/62-m7-performance-ti`
- Issue: #62

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
| Orchestrator unit tests | 122 passed |
| tests/run.sh | 114 passed |
| tests/evals/run.sh | 39 passed |

## Spot checks

- `item_from_execution_run` → `kind: performance` + `performance_metrics`
- Plan renders `## Performance Context` (empty when no matches)
- `COMPASS_TI_PROVIDER=github-stars` selects `GithubStarsTechnologyIntelligenceProvider`
- Golden fixtures under `tests/fixtures/ti/github-stars-recorded/` (no network in CI)
- Registry compiles 33 Skills including `technology-intelligence-live`
