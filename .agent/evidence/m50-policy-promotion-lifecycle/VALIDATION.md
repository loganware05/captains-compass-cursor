# M50 Validation Evidence

| Item | Result |
|---|---|
| Plan | `m50-policy-promotion-lifecycle` APPROVED 2026-10-11 |
| Linear | OVA-66 |
| Branch | `feature/OVA-66-m50-policy-promotion-lifecycle` |
| Rollback | `rollback/pre-m50-policy-promotion` @ `dad671f` |
| VERSION | 1.55.0 |

## Tests

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_m50_policy_promotion.py' -v
# 14 tests OK

PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_m48*.py' -v
# 12 OK

PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_m49*.py' -v
# 15 OK

./scripts/doctor.sh
# Doctor passed: 0 errors
```

## Invariants checked

- `COMPASS_POLICY_PROMOTE_ENABLED` unset → CLI exit 2
- Shadow reports `applied: false` (schema-const)
- Schemas reject `approved_for_execution: true`
- Materialize proposals do not create `.cursor/`
- Active compose-include requires `COMPASS_POLICY_APPLY_ENABLED`
