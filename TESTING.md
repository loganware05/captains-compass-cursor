# Testing

## What we test

1. **Doctor script** — expected files, rule frontmatter, Skill structure, hooks,
   failClosed policy, budget templates, VERSION, control CI workflow, orchestrator
   schemas, capability registry compile, TI integration doc, experience layout,
   record-execution-run script
2. **Installer** — copies workflow into a temporary Git repo; refuses overwrite without `--force`;
   creates `.agent/budgets/`, `.agent/capabilities/compiled/`, `.agent/plans/`,
   `.agent/experience/`, and budget templates
3. **Hooks** — secret protection, protected-branch, plan-approval allow/deny cases,
   branch-name, PR evidence; failClosed critical/soft split
4. **Sandbox exercise (manual)** — approval gate, then implement after approval;
   budget stop when limits hit

## Automated tests (local)

```bash
./scripts/doctor.sh
./tests/run.sh
./tests/evals/run.sh
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

File TI (offline fixtures; still NOT APPROVED FOR EXECUTION):

```bash
COMPASS_TI_PROVIDER=file ./scripts/capability-plan.sh --plan-id ti-demo "accessible forms"
```

Record ExecutionRun + Experience:

```bash
./scripts/record-execution-run.sh \
  --plan-id my-feature \
  --outcome success \
  --objective "summary" \
  --skills "execution-telemetry,pull-request-preparation"
```

Promote candidate / train from Experience (staging drafts only):

```bash
./scripts/promote-candidate.sh --candidate path/to/candidate.json --draft-skill draft-slug
./scripts/train-skill-from-experience.sh --experience path/to/experience.json --skill-slug draft-slug
```

Persistent-role proposal (staging + PR only):

```bash
./scripts/propose-persistent-role.sh --agent-id compass-evaluator
```

Captain-flagged weight apply (bounded Level 3):

```bash
# After editing proposal to set "captain_approved": true
./scripts/apply-routing-proposal.sh \
  --proposal .agent/routing/proposals/<id>.json \
  --budget .agent/budgets/<plan-id>.md
```

Knowledge Steward ingest and query (explicit CLI only):

```bash
./scripts/ingest-knowledge.sh --from-store experience,evaluations,decisions
./scripts/ingest-knowledge.sh --from-store runs,experience
./scripts/ingest-knowledge.sh --from-store decisions --rebuild-vector
./scripts/rebuild-knowledge-vector-index.sh
./scripts/query-knowledge.sh --query "evaluator routing" --kind decision
./scripts/query-knowledge.sh --query "matcher tuning" --mode hybrid
./scripts/query-knowledge.sh --query "execution retries" --kind performance
```

Live Technology Intelligence (Captain local; gh auth required):

```bash
COMPASS_TI_PROVIDER=github-stars \
  ./scripts/query-technology-intelligence.sh --query "accessible react forms"
COMPASS_TI_PROVIDER=github-stars \
  ./scripts/capability-plan.sh --plan-id ti-live-demo "accessible react forms"
```

## Evidence matrix

Required validation artifacts by change type:
[`docs/EVIDENCE_MATRIX.md`](docs/EVIDENCE_MATRIX.md).

## Harness evals

Deterministic sensors (CI + local):

```bash
./tests/evals/run.sh
```

Evals cover: failClosed policy, plan-approval gate, soft-hook skips, orchestrator schema
presence, stub and file Technology Intelligence isolation, record-execution-run smoke,
golden fixture determinism, and enhanced plan template sections.

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
