# M53 Validation Evidence — Prompt/Policy Provenance + Behavior Exemplars

- **Plan:** `m53-prompt-policy-provenance`
- **Linear:** OVA-69
- **Release:** v1.58.0
- **Branch:** `feature/OVA-69-m53-prompt-policy-provenance`
- **Rollback:** `rollback/pre-m53-prompt-policy-provenance` @ `448ac25`
- **Date:** 2026-10-11

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator \
  -p 'test_m53_prompt_policy_provenance.py' -v

env -u COMPASS_PROVENANCE_ENABLED ./scripts/run-provenance.sh list --repo-root .
# expect exit 2 + COMPASS_PROVENANCE_ENABLED

COMPASS_PROVENANCE_ENABLED=1 ./scripts/northstar provenance list --repo .
COMPASS_PROVENANCE_ENABLED=1 ./scripts/northstar examples list --repo .
```

## Results (2026-10-11)

| Check | Result |
|---|---|
| `test_m53_prompt_policy_provenance` (10 tests) | PASS |
| Provenance fail-closed without gate | PASS (exit 2) |
| Schema locks (`approved_for_execution` / `auto_promoted` false) | PASS |
| Exemplar draft never creates `.cursor/skills` | PASS |
| Live providers required | No |
| `./scripts/doctor.sh` | PASS (0 errors, 0 warnings) |

## Authority

- Provenance / exemplars: `approved_for_execution: false`, `authority_mutation: false`
- Exemplars: `auto_promoted: false` (proposal-only)
