# Testing

## What we test

1. **Doctor script** — expected files, rule frontmatter, Skill structure, hooks,
   failClosed policy, budget templates, VERSION, control CI workflow
2. **Installer** — copies workflow into a temporary Git repo; refuses overwrite without `--force`;
   creates `.agent/budgets/` and budget templates
3. **Hooks** — secret protection, protected-branch, plan-approval allow/deny cases,
   branch-name, PR evidence; failClosed critical/soft split
4. **Sandbox exercise (manual)** — approval gate, then implement after approval;
   budget stop when limits hit

## Automated tests (local)

```bash
./scripts/doctor.sh
./tests/run.sh
```

Orchestrator schema unit tests (included in `tests/run.sh`):

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_*.py' -v
```

Capability resolve CLI:

```bash
./scripts/capability-resolve.sh "Build a React dashboard with tests"
```

Task graph planner:

```bash
./scripts/plan-task-graph.sh "Build a React dashboard with tests"
```

Agent manifest builder:

```bash
./scripts/build-agent-manifests.sh "Build a React dashboard with tests" draft-plan-id
```

Full capability-aware plan sections:

```bash
./scripts/capability-plan.sh --plan-id my-feature "Build a React dashboard with tests"
```

## Evidence matrix

Required validation artifacts by change type:
[`docs/EVIDENCE_MATRIX.md`](docs/EVIDENCE_MATRIX.md).

## Harness evals

Deterministic sensors (CI + local):

```bash
./tests/evals/run.sh
```

Manual sandbox behavioral checklist:
[`docs/evals/SANDBOX_BEHAVIORAL_CHECKLIST.md`](docs/evals/SANDBOX_BEHAVIORAL_CHECKLIST.md).

## Control-repo CI

GitHub Actions (`.github/workflows/ci.yml`) runs the same commands on every
pull request and push to `main`:

1. `./scripts/doctor.sh`
2. `./tests/run.sh`

## Manual sandbox checklist

See [docs/SANDBOX_VALIDATION.md](docs/SANDBOX_VALIDATION.md).

Install verification for the disposable sandbox was completed during the V0.1 build.
Cursor approval-gate and failure exercises must be run interactively in that sandbox.

## Deliberate failure tests

See design doc Part 9 and `docs/SANDBOX_VALIDATION.md`. All six exercises passed 2026-07-14 (evidence under `.agent/evidence/sandbox-failure-tests/`): bypass approval, scope expansion, failing test, hard-coded secret, parallel conflict, budget stop.
