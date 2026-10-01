# M46 Behavior Intelligence Foundation — Validation

## Plan

- Plan ID: `m46-behavior-intelligence-foundation`
- Status: APPROVED (Captain 2026-10-01)
- Issue: OVA-58
- Rollback: `rollback/pre-m46-behavior-intelligence` @ `0d125c7`
- Release: v1.46.0

## Commands

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m46_behavior_evaluation -v
./tests/run.sh
```

## Results

| Check | Result |
|---|---|
| doctor | passed (0 errors) |
| test_m46_behavior_evaluation | 15/15 OK |
| authority_mutation always false | covered |
| enable flag default off | covered |
| dual ledger JSON + JSONL | covered |
| CSV non-canonical | covered |
| no Skill/routing mutation | covered |

## Operator smoke (optional)

```bash
COMPASS_BEHAVIOR_EVAL_ENABLED=1 \
COMPASS_DECISION_PROVIDER=file \
./scripts/northstar evaluate run run-fixture-contact-counter --repo /tmp/m46-demo
```

## Security notes

- No secrets in packets/ledger
- Jev path reuses Typesafe allowlist + pinned `jev-1.13.0`
- Fail closed on abstain/error
- Observe-only — no authority mutation

## Adversarial fixes (iteration 2)

- Skip `evaluations/behavior/**` in Knowledge Steward ingest (M3 isolation)
- Redact secrets in packet objectives before persist
- `find_by_execution` prefers newest `created_at`
- Dual-write: temp JSON → JSONL append → atomic rename; repair missing JSONL
