# Validation — xrv-readiness-assessor (#263)

| Item | Value |
|---|---|
| Plan | `xrv-readiness-assessor` |
| Release | **v1.84.0** |
| Rollback | `rollback/pre-xrv-readiness-assessor` @ `cb85c4a` |

## Commands

```bash
COMPASS_XRV_READINESS_ENABLED=1 ./scripts/northstar assess readiness --repo .
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_xrv_readiness_assessor -v
./scripts/doctor.sh
./tests/run.sh
```

## Results (2026-11-11)

- Doctor: passed
- Unit tests (`test_xrv_readiness_assessor` + release integrity): OK
- `./tests/run.sh`: exit 0

## Authority

- `approved_for_execution: false`
- `authority_mutation: false`
- `auto_promoted: false`
- `scores_invented: false`
