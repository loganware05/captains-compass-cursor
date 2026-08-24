# M6 validation evidence

Plan: `m6-vector-experience-store`  
Issue: #58  
Branch: `feature/58-m6-vector-experience-store`  
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
| Unit tests (orchestrator) | 111 passed |
| Doctor | 0 errors, 0 warnings |
| Evals | 39 passed |
| tests/run.sh | 114 passed, 0 failed |

## Captain decisions verified

- Plan-writer hybrid when vector index exists
- Dedicated `rebuild-knowledge-vector-index.sh` + ingest `--rebuild-vector`
- Performance ingest deferred to M7
- stdlib TF-IDF only (no production vector DB)
