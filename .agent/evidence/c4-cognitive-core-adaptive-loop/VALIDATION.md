# Validation — c4-cognitive-core-adaptive-loop

| Field | Value |
|---|---|
| Plan ID | `c4-cognitive-core-adaptive-loop` |
| Issue | [#208](https://github.com/loganware05/captains-compass-cursor/issues/208) |
| Branch | `cursor/208-c4-adaptive-loop-64df` |
| Rollback | `rollback/pre-c4-cognitive-core-adaptive-loop` @ `9f78bda` |
| Date | 2026-10-17 |

## Checks

| Check | Result |
|---|---|
| Unit `test_c4_cognitive_core_adaptive_loop.py` | PASS (8) |
| C3 regression + schemas | PASS |
| `./scripts/doctor.sh` | PASS (cycle schemas + fail-closed) |
| CLI lifecycle begin→checkpoint→close→review | PASS |
| Adversarial smoke (security objective) | PASS — begin `high`; checkpoint friction `very_high`; `scope_expanded: false`; drafts `auto_promoted: false` |

## Security / authority

- Schemas lock `approved_for_execution` / `authority_mutation` to false
- Gate fail-closed without `COMPASS_CYCLE_ENABLED`
- Begin requires `COMPASS_ASSESS_ENABLED` (does not bypass C3 gate)
- Checkpoints cannot set `scope_expanded: true`
- Close drafts proposals only; Learning Review never installs/activates

## Rollback

```bash
git checkout main
git reset --hard rollback/pre-c4-cognitive-core-adaptive-loop
```
