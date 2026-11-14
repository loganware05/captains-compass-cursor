# Validation — post-merge-wave-continue (#274)

## Scope

Waves A+B: Skill `post-merge-wave-continue`, wave ledger schema/CLI,
handbook/rule cross-links, doctor assertions. Wave C: poll-pattern docs only.

## Commands (fresh this session)

```bash
./scripts/build-skill-inodes.sh
./scripts/doctor.sh
./scripts/northstar evidence drift --repo .
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_plan_waves \
  tests.orchestrator.test_registry -v
./tests/run.sh
```

## Results

| Check | Result |
|---|---|
| Doctor | PASS (0 errors; warning: carry_over_pending_captain on edited Skills) |
| Release drift VERSION↔README | ok (`1.87.0`) |
| Unit `test_plan_waves` | 9/9 PASS |
| Unit `test_registry` (52 skills) | PASS |
| `tests/run.sh` | see `tests-run.txt` |

## Authority locks

- Ledger `approved_for_execution: false`, `authority_mutation: false`,
  `auto_merge: false` (schema const)
- CLI refuses DRAFT plans, OPEN PRs, empty remaining waves, `pause_between_waves`

## Evidence files

- `doctor.txt`
- `unit-tests.txt`
- `tests-run.txt`
- `release-drift.json`
- `SECURITY.md`

## Rollback

Tag `rollback/pre-post-merge-wave-continue` @ `9e2c0d1`
