# Validation — xrv-release-integrity (#261)

| Item | Value |
|---|---|
| Plan | `xrv-release-integrity` |
| Release | **v1.83.1** |
| Baseline / rollback | `rollback/pre-xrv-release-integrity` @ `987a49c` |
| Branch | `feature/261-xrv-release-integrity` |

## Commands

```bash
./scripts/run-xrv-eer.sh drift --repo-root .
COMPASS_XRV_EER_ENABLED=1 ./scripts/run-xrv-eer.sh validate --repo-root .
./scripts/doctor.sh
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_xrv_release_integrity -v
./tests/run.sh
```

## Authority locks

EER fixture and validate path keep:

- `approved_for_execution: false`
- `authority_mutation: false`
- `issues_auto_closed: false`
- `auto_promoted: false`

## Results (2026-11-10)

- Doctor: passed (0 errors)
- `tests.orchestrator.test_xrv_release_integrity`: 5/5 OK
- `./tests/run.sh`: exit 0
- EER fixture validates under `COMPASS_XRV_EER_ENABLED=1`
- Drift check clean at VERSION=README=1.83.1

## Notes

- I1–I6 GitHub issues left open for Captain confirmation (no auto-close).
- TrapHouse / Bitcoin product work is out of scope for this PR (handoff threads).
