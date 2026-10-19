# Validation — c7-cognitive-core-training-bridge

| Field | Value |
|---|---|
| Plan ID | `c7-cognitive-core-training-bridge` |
| Issue | [#217](https://github.com/loganware05/captains-compass-cursor/issues/217) |
| Branch | `cursor/217-c7-training-bridge-64df` |
| Rollback | `rollback/pre-c7-cognitive-core-training-bridge` @ `f16e8bb` |
| Date | 2026-10-19 |

## Checks

| Check | Result |
|---|---|
| Unit `test_c7_cognitive_core_training_bridge.py` | PASS (12) |
| `./scripts/doctor.sh` | PASS (train schemas + fail-closed + layout) |
| CLI export smoke | PASS — `--fixture`, `run_mode=fixture`, authority false, dual-write store+`--out` |
| CLI review smoke | PASS — review by `--export-id` and `--export-path`; blocked until gates |

## Security / authority

- Schemas lock `approved_for_execution` / `authority_mutation` / `auto_uploaded` false
- Gate fail-closed without `COMPASS_TRAIN_BRIDGE_ENABLED`
- Incomplete permission checklist refuses export
- Secret-shaped trajectory text redacted via `decision.state.redact_text`
- Distinct from Experience→Skill drafts; cites `from_experience.py` only
- Never uploads or changes live weights

## Rollback

```bash
git checkout main
git reset --hard rollback/pre-c7-cognitive-core-training-bridge
```
