# Validation — i2-t3-execution-adapter (#251)

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_i2_t3*.py' -v
./scripts/doctor.sh
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 start \
  --plan-id i2-t3-execution-adapter --objective "fixture" --allow-fixture-plan
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
```

## Results

- Unit tests: 8/8 pass
- Doctor: 0 errors
- Overseer snapshot included `execution_refs` and `dev-t3-executions`
