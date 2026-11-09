# Validation — i5-workos-identity (#257)

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_i5_workos*.py' -v
COMPASS_IDENTITY_ENABLED=1 ./scripts/northstar identity sync
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
./scripts/doctor.sh
```

## Results

- Unit tests: 4/4 pass
- Fixture packet: `workos-identity-7054ac8270f0`
- Overseer snapshot: `psnap-5ea0b992a310` with `identity_refs` + `dev-workos-identity`
- Doctor: 0 errors
