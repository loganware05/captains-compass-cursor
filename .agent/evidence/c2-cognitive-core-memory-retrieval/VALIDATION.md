# Validation — c2-cognitive-core-memory-retrieval

| Field | Value |
|---|---|
| Plan ID | `c2-cognitive-core-memory-retrieval` |
| Issue | [#203](https://github.com/loganware05/captains-compass-cursor/issues/203) |
| Branch | `cursor/203-c2-memory-retrieval-64df` |
| Rollback | `rollback/pre-c2-cognitive-core-memory-retrieval` @ `2314def` |
| Date | 2026-10-17 |

## Checks

| Check | Result |
|---|---|
| Unit `test_c2_cognitive_core_memory_retrieval.py` | PASS (11 tests) |
| Gold-set 30q evidence-linked ≥90% + expect kinds + negatives | PASS |
| C1 regression `test_c1_cognitive_core_source_of_truth.py` | PASS (10 tests) |
| `./scripts/doctor.sh` | PASS (0 errors); `brain-context-response.schema.json` present |
| CLI smoke `brain context --query` | PASS — cites ADR-079 / ADR-077; authority flags false |
| Gate fail-closed without `COMPASS_BRAIN_ENABLED` | PASS |

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator \
  -p 'test_c2_cognitive_core_memory_retrieval.py' -v

./scripts/doctor.sh

COMPASS_BRAIN_ENABLED=1 \
./scripts/northstar brain context --query "Cognitive Core memory retrieval ADR" \
  --mode keyword --top 5 --repo .
```

## Security / authority

- `approved_for_execution: false` and `authority_mutation: false` schema-const
- No secret paths ingested; context is read-only compose
- Live embeddings not required for CI (keyword mode)

## Rollback

```bash
git checkout main
git reset --hard rollback/pre-c2-cognitive-core-memory-retrieval
```
