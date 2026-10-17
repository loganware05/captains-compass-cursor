# Validation — c3-cognitive-core-difficulty-fit

| Field | Value |
|---|---|
| Plan ID | `c3-cognitive-core-difficulty-fit` |
| Issue | [#205](https://github.com/loganware05/captains-compass-cursor/issues/205) |
| Branch | `cursor/205-c3-difficulty-fit-64df` |
| Rollback | `rollback/pre-c3-cognitive-core-difficulty-fit` @ `f1ae35d` |
| Date | 2026-10-17 |

## Checks

| Check | Result |
|---|---|
| Unit `test_c3_cognitive_core_difficulty_fit.py` | PASS (12) |
| Backtest bands (`assess-backtest/cases.json`) | PASS |
| C2 regression | PASS |
| Schema registry (`test_schemas`) | PASS |
| `./scripts/doctor.sh` | PASS (assess schema + fail-closed) |
| CLI smoke `assess project` | PASS — band/score present; authority flags false |

## Security / authority

- Schema locks `approved_for_execution` / `authority_mutation` to false
- Gate fail-closed without `COMPASS_ASSESS_ENABLED`
- Advisory recommendations only — no plan-status mutation

## Rollback

```bash
git checkout main
git reset --hard rollback/pre-c3-cognitive-core-difficulty-fit
```
