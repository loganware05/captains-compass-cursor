# Validation — i6-cross-provider-validation (#259)

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_i6_cross*.py' -v
COMPASS_I6_VALIDATE_ENABLED=1 ./scripts/northstar validate integrations
./scripts/doctor.sh
```

## Results

- Unit tests: 2/2 pass
- Scorecard: `i6-score-1f395b7d33f8` — passed=5 failed=0
- Doctor: 0 errors
