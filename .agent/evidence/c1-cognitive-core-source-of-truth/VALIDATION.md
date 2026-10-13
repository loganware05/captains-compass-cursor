# C1 Cognitive Core Source of Truth — Validation Evidence

- Plan: `c1-cognitive-core-source-of-truth` (OVA-72)
- Branch: `feature/OVA-72-c1-cognitive-core-source-of-truth`
- Rollback: `rollback/pre-c1-cognitive-core-source-of-truth` @ `9b9d6bd`
- VERSION: **1.60.0**
- Date: 2026-10-13

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_c1_cognitive_core_source_of_truth.py' -v
./scripts/doctor.sh
env -u COMPASS_BRAIN_ENABLED ./scripts/northstar brain sync --repo .
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain sync --repo .
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain status --repo .
```

## Results

| Check | Result |
|---|---|
| C1 unittest (10) | PASS |
| Doctor | PASS (0 errors) — schema + fail-closed brain gate |
| Gate unset | exit 2, mentions `COMPASS_BRAIN_ENABLED` |
| Sync | Writes `.agent/project-state/` + `fresh` |
| Status after sync | `fresh` when HEAD matches |
| Stale after new commit | Covered by unittest |

## Invariants

- CI does not require live GitHub / Kimi
- Canonical memory docs not auto-rewritten
- `approved_for_execution: false` / `authority_mutation: false`
- Local-git-only for C1 (GitHub deferred)
