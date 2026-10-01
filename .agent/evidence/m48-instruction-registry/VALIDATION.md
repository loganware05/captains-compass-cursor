# M48 Instruction Registry + Prompt Composer — Validation

## Plan

- Plan ID: `m48-instruction-registry`
- Status: APPROVED (Captain 2026-10-01)
- Issue: OVA-60
- Rollback: `rollback/pre-m48-instruction-registry` @ `402573e`
- Release: v1.48.0

## Commands

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m48_instruction_registry -v
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m47_behavior_pattern_learning tests.orchestrator.test_m46_behavior_evaluation -v
./tests/run.sh
```

## Results

| Check | Result |
|---|---|
| doctor | passed (0 errors, 0 warnings) |
| test_m48_instruction_registry | 11/11 OK |
| M46/M47 regression | 35/35 OK |
| full suite | 125 passed |
| enable flag default off | covered |
| PICCO hash deterministic | covered |
| draft-from-candidates proposal-only | covered |
| evaluate records prompt_bundle_hash | covered |
| no `.cursor/` mutation | covered |

## Security notes

- Proposal-only locks on instruction + bundle schemas
- Enable flag default off
- Evaluate hash is record-only (no live prompt injection)
- Distinct from `northstar skills learn`
