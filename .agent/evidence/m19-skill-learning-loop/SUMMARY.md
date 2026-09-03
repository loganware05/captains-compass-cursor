# M19 validation evidence

## Commands

```bash
./scripts/doctor.sh
./scripts/compile-capability-registry.sh
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m19_skill_learning_loop tests.orchestrator.test_m18_sandbox_release_smokes -q
./scripts/run-skill-learning-loop.sh --source fixtures --objective "accessible react forms" --top 1
./tests/run.sh
./tests/evals/run.sh
```

## Results

| Check | Result |
|---|---|
| Doctor | Pass (0 errors) |
| Registry compile | Pass |
| M19 unit tests | Pass (7) |
| M18 smoke catalog tests | Pass |
| Learning loop CLI (fixtures) | Pass — improve-existing → `react-engineering` proposal + drafts |
| `./tests/run.sh` | 116 passed, 0 failed |
| `./tests/evals/run.sh` | 42 passed, 0 failed |

## Safety checks

- `approved_for_execution` remains false
- No auto-write into `.cursor/skills/` for draft slugs
- `AVAILABLE_SKILL` still requires `--captain-approved`
- Improvement proposals are proposal-only under `.agent/capabilities/candidates/skill-improvement-proposals/`

## Rollback

`rollback/pre-m19-skill-learning` @ `3c4455e`
