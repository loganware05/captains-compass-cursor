# E2E Cognitive Core evaluation — validation

| Check | Result |
|---|---|
| Unit tests `test_e2e_cognitive_core_evaluation` | Pass (6) |
| Regression C6+C7 unit tests | Pass |
| Doctor | 0 errors, 0 warnings |
| Hermetic `run-cognitive-core-e2e.sh --enable-gates` | overall **pass** |
| Authority flags | always false |
| `auto_uploaded` | false |

## Baselines (control repo hermetic run)

| Metric | Value |
|---|---|
| brain_goldset_rate | 1.0 (target 0.9) |
| assess_backtest_pass_rate | 1.0 |
| route_eval_case_count | 3 |
| cycle_authority_locked | true |
| rea_claim_kinds_ok | true |
| train_auto_uploaded | false |

See `SUMMARY.md`, `LATEST.json`, and `e2e-cc-*.json`.
