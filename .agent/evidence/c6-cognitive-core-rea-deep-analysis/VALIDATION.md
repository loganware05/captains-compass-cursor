# Validation — c6-cognitive-core-rea-deep-analysis

| Field | Value |
|---|---|
| Plan ID | `c6-cognitive-core-rea-deep-analysis` |
| Issue | [#214](https://github.com/loganware05/captains-compass-cursor/issues/214) |
| Branch | `cursor/214-c6-rea-deep-analysis-64df` |
| Rollback | `rollback/pre-c6-cognitive-core-rea-deep-analysis` @ `735cb6a` |
| Date | 2026-10-19 |

## Checks

| Check | Result |
|---|---|
| Unit `test_c6_cognitive_core_rea_deep_analysis.py` | PASS (10) |
| C5 + schema regression | PASS |
| `./scripts/doctor.sh` | PASS (rea schema + fail-closed) |
| CLI fixture smoke | PASS — `run_mode=fixture`, authority false, hypothesis present |

## Security / authority

- Schema locks `approved_for_execution` / `authority_mutation` false
- Gate fail-closed without `COMPASS_REA_ENABLED`
- Live path requires complete checklist + `--allow-live`; auto-execution withheld
- Forbidden speculative training-data recovery questions refused

## Rollback

```bash
git checkout main
git reset --hard rollback/pre-c6-cognitive-core-rea-deep-analysis
```
