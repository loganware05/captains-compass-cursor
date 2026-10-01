# M47 Behavior Pattern Learning — Validation

## Plan

- Plan ID: `m47-behavior-pattern-learning`
- Status: APPROVED (Captain 2026-10-01)
- Issue: OVA-59
- Rollback: `rollback/pre-m47-behavior-pattern-learning` @ `cb4f463`
- Release: v1.47.0

## Commands

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m47_behavior_pattern_learning -v
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m46_behavior_evaluation -v
./tests/run.sh
```

## Results

| Check | Result |
|---|---|
| doctor | passed (0 errors, 0 warnings) |
| test_m47_behavior_pattern_learning | 18/18 OK |
| test_m46_behavior_evaluation (regression) | 17/17 OK |
| min_occurrence default 3 | covered |
| polarity praise/friction | covered |
| candidates proposal-only | covered |
| enable flag default off | covered |
| no Skill/routing/Policy mutation | covered |
| stale pattern prune on rescan | covered |
| schema additionalProperties false | covered |
| created_at preserved on overwrite | covered |

## Operator smoke (optional)

```bash
COMPASS_BEHAVIOR_LEARN_ENABLED=1 \
./scripts/northstar learn scan --repo .
./scripts/northstar learn list --repo .
```

## Security notes

- Reads M46 ledger only (redaction inherited)
- Candidates cannot grant authority
- Enable flag default off
- Distinct from `northstar skills learn`

## Adversarial fixes (iteration 2)

- Prune stale pattern/candidate JSON when they fall below min_occurrence
- Schemas: `additionalProperties: false`; pattern requires
  `approved_for_execution: false`
- Preserve `created_at` on overwrite; set `updated_at`
