# M20 validation evidence

## Commands

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m20_experience_bridge -q
./tests/run.sh
```

## Results

| Check | Result |
|---|---|
| Doctor | Pass |
| M20 unit tests | 7 passed |
| `./tests/run.sh` | 118 passed, 0 failed |

## Safety

- Experience bridge does not promote to PROVEN without `--captain-approved` and threshold
- Improvement apply refuses without `--captain-approved`
- Default apply writes drafts only; `--apply-live` required to touch live Skills
- Excluded Skills (e.g. `security-review`) cannot be applied
