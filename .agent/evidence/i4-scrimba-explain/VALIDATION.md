# Validation — i4-scrimba-explain (#255)

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_i4_scrimba*.py' -v
COMPASS_EXPLAIN_ENABLED=1 ./scripts/northstar explain create --topic "How NorthStar approval gates work"
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
./scripts/doctor.sh
```

## Results

- Unit tests: 4/4 pass
- Fixture packet: `scrimba-explain-768f714e9d6a`
- Overseer snapshot: `psnap-871cf1161afd` with `explainer_refs` + `dev-scrimba-explainers`
- Doctor: 0 errors
