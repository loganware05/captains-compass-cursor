# M11 validation evidence

Plan: `m11-embeddings-package-ti`  
Issue: #78  
Branch: `feature/78-m11-embeddings-package-ti`  
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
| Unit tests (orchestrator) | 147 passed |
| Doctor | 0 errors, 0 warnings |
| Evals | 39 passed |
| tests/run.sh | 114 passed, 0 failed |

## Captain decisions verified

- v1.15.0 target
- Both fixture embeddings and package-registry file TI
- Fixture + protocol only (no live embedding HTTP)
- TF-IDF always fallback
- Dedicated Skills `embedding-providers` + `package-registry-ti` (38 Skills)
