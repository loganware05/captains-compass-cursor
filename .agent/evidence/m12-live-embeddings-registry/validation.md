# M12 validation evidence

Plan: `m12-live-embeddings-registry`  
Issue: #82  
Branch: `feature/82-m12-live-embeddings-registry`  
Date: 2026-08-24

## Commands

```bash
./scripts/compile-capability-registry.sh
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_*.py' -q
./scripts/doctor.sh
./tests/evals/run.sh
./tests/run.sh
```

## Results

| Check | Result |
|---|---|
| Unit tests (orchestrator) | 153 passed |
| Doctor | 0 errors, 0 warnings |
| Evals | 40 passed |
| tests/run.sh | 114 passed, 0 failed |

## Captain decisions verified

- v1.16.0 target
- Both openai-compatible embeddings and live package-registry TI
- `COMPASS_EMBEDDING_*` env names
- npm + PyPI live ecosystems
- Extend existing Skills only
- Soft-hook `.agent/compass-skip.env` inheritance
