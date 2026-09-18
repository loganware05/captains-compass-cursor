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

Finding outcomes → Experience (M31; hermetic fixture path):

```bash
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m31_finding_outcomes -v
./scripts/record-finding-outcomes.sh \
  --report .agent/evidence/m28-reviewer-specialist-composition/bitcoin-style-demo/report.json \
  --triage tests/fixtures/code-review/triage-outcomes.json \
  --plan-id m31-finding-outcomes-experience \
  --emit-routing-proposal
./scripts/northstar outcomes record \
  --report .agent/evidence/m28-reviewer-specialist-composition/bitcoin-style-demo/report.json \
  --triage tests/fixtures/code-review/triage-outcomes.json
```

Repair loop FIND→PROVE→packet (M32 / B4; hermetic; never auto-merge):

```bash
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m32_b4_repair_loop -v
./scripts/start-repair-loop.sh \
  --report tests/fixtures/repair/sandbox-report.json \
  --finding finding-sandbox-secrets-1 \
  --run-id b4-sandbox-fixture-demo \
  --repository loganware05/captain-compass-sandbox \
  --captain-authorized-fix
./scripts/northstar repair start \
  --report tests/fixtures/repair/sandbox-report.json \
  --finding finding-sandbox-secrets-1 \
  --repository loganware05/captain-compass-sandbox
```

Precision ledger (M33 / B5; hermetic; proposal-only):

```bash
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m33_b5_precision_ledger -v
./scripts/aggregate-precision-ledger.sh \
  --outcomes tests/fixtures/code-review/precision-outcomes.json \
  --ledger-id b5-fixture-demo \
  --emit-priority-proposal
./scripts/northstar precision aggregate \
  --outcomes tests/fixtures/code-review/precision-outcomes.json \
  --ledger-id b5-cli-demo
```

Filesystem-gated context (M40; hermetic; deterministic):

```bash
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m40_context_inodes -v
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m40_skill_inodes -v
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m40_dependency_graph -v
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m40_boundary_gate -v
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m40_manifest_pwd -v

# Inode store + context tree (deterministic build; --check fails closed on stale)
./scripts/build-context-inodes.sh
./scripts/build-context-inodes.sh --check
./scripts/walk-context-route.sh --route orchestrator/review
./scripts/northstar context build --repo /path/to/repo
./scripts/northstar context walk --repo /path/to/repo --route src/lib

# Content-addressed Skill inodes (carry-over is Captain-gated)
./scripts/build-skill-inodes.sh
./scripts/build-skill-inodes.sh --check
./scripts/build-skill-inodes.sh --captain-approved   # approve reputation carry-over

# Boundary review gate (default on; skips with note when inode store absent/stale)
./scripts/run-code-review.sh --repo-root /path/to/repo --base main
./scripts/run-code-review.sh --repo-root /path/to/repo --no-boundary-check
```

Single launcher UX (M34 / C1; hermetic help + docs index):

```bash
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m34_c1_single_launcher_ux -v
./scripts/northstar help
test -f docs/INDEX.md
```

Promote candidate / train from Experience (staging drafts only):

```bash
./scripts/promote-candidate.sh --candidate path/to/candidate.json --draft-skill draft-slug
./scripts/promote-candidate.sh --candidate path/to/staging.json \
  --stage APPROVED --evidence .agent/evidence/approval.md --captain-approved \
  --skill-slug my-skill
./scripts/promote-candidate.sh --candidate path/to/staging.json \
  --stage AVAILABLE_SKILL --evidence .agent/evidence/approval.md --captain-approved \
  --skill-slug my-skill
./scripts/train-skill-from-experience.sh --experience path/to/experience.json --skill-slug draft-slug
```

Skill learning loop (M19 — fixtures default; ti-cache/live Captain-local):

```bash
./scripts/run-skill-learning-loop.sh --source fixtures --objective "accessible react forms"
./scripts/run-skill-learning-loop.sh --source ti-cache --objective "schema validation"
./scripts/run-skill-learning-loop.sh --source fixtures --category design-system \
  --objective "design system craft tokens"
./scripts/example-design-repo-scorecard.sh
./scripts/run-skill-learning-loop.sh --source fixtures --record-experiences \
  --objective "accessible react forms"
./scripts/bridge-learning-experiences.sh --run .agent/learning-runs/<id>.json
./scripts/apply-skill-improvement.sh --proposal path/to/proposal.json --captain-approved
```

NorthStar connected routine (M21 fixtures + M22 live doubles; no live credentials):

```bash
./scripts/run-northstar-routine.sh --demo
./scripts/run-northstar-routine.sh --demo --approve --advance-to-review
./scripts/run-northstar-routine.sh --demo --approve --advance-to-review \
  --propose-roles --surface-routing --notion-mode fixtures
./scripts/run-northstar-routine.sh --event tests/fixtures/northstar/slack-objective.json --provider slack
./scripts/reconcile-northstar-run.sh --run .agent/evidence/<run_id>/run.json
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m21_northstar -v
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m22_northstar_live -v
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_issue50*.py' -v
./scripts/serve-northstar-ingress.sh --mode fixtures   # /healthz only; webhooks 503
```

See `docs/integrations/northstar-live-ops.md`.

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
./scripts/refresh-ti-cache.sh
COMPASS_TI_PROVIDER=github-stars-cached \
  ./scripts/query-technology-intelligence.sh --query "accessible react forms"
```

Procedure playbook ingest:

```bash
./scripts/ingest-knowledge.sh --from-store procedures
./scripts/query-knowledge.sh --query "bounded autonomy" --kind procedure
```

External Notion / NotebookLM file ingest:

```bash
./scripts/ingest-knowledge.sh --from-store notion,notebooklm
./scripts/query-knowledge.sh --query "approval gate" --kind knowledge
```

Hugging Face file TI + stale-aware cache refresh:

```bash
COMPASS_TI_PROVIDER=huggingface-file \
  ./scripts/query-technology-intelligence.sh --query "sentence embeddings"
./scripts/refresh-ti-cache.sh --if-stale 24
```

Fixture dense embeddings (TF-IDF remains fallback):

```bash
COMPASS_EMBEDDING_PROVIDER=fixture \
  ./scripts/rebuild-knowledge-embedding-index.sh
COMPASS_EMBEDDING_PROVIDER=fixture \
  ./scripts/query-knowledge.sh --query "matcher tuning" --mode vector
```

Package-registry file TI:

```bash
COMPASS_TI_PROVIDER=package-registry-file \
  ./scripts/query-technology-intelligence.sh --query "schema validation"
```

Live package-registry TI (Captain local; never CI):

```bash
COMPASS_TI_PROVIDER=package-registry \
  ./scripts/query-technology-intelligence.sh --query "schema validation"
```

OpenAI-compatible embeddings (Captain local; never CI):

```bash
export COMPASS_EMBEDDING_PROVIDER=openai-compatible
export COMPASS_EMBEDDING_API_KEY=...   # never commit
./scripts/rebuild-knowledge-embedding-index.sh
```

Soft-hook skip-env file (when Cursor does not forward process env):

```bash
printf 'COMPASS_SKIP_FORMAT=1\n' > .agent/compass-skip.env
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
