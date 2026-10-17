# Validation — c5-cognitive-core-adaptive-routing

| Field | Value |
|---|---|
| Plan ID | `c5-cognitive-core-adaptive-routing` |
| Issue | [#211](https://github.com/loganware05/captains-compass-cursor/issues/211) |
| Branch | `cursor/211-c5-adaptive-routing-64df` |
| Rollback | `rollback/pre-c5-cognitive-core-adaptive-routing` @ `d8f1ac4` |
| Date | 2026-10-17 |

## Checks

| Check | Result |
|---|---|
| Unit `test_c5_cognitive_core_adaptive_routing.py` | PASS (10) |
| C4 + schema regression | PASS |
| `./scripts/doctor.sh` | PASS (route schemas + fail-closed) |
| CLI `model route` + `model evaluate` | PASS |
| Adversarial smoke (security objective) | PASS — `premium` / `reasoning-strong`; `auto_switched: false` |

## Security / authority

- Schemas lock `approved_for_execution` / `authority_mutation` / `auto_switched` false
- Gate fail-closed without `COMPASS_ROUTE_ENABLED`
- Evaluate is hermetic fixture-only (no live model/API)
- Does not bind Cursor model settings or auto-spend

## Rollback

```bash
git checkout main
git reset --hard rollback/pre-c5-cognitive-core-adaptive-routing
```
