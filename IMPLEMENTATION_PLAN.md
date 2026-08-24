# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m7-performance-ti
- Issue: [#62](https://github.com/loganware05/captains-compass-cursor/issues/62) — M7: Performance knowledge ingest + live GitHub Stars TI (v1.11.0)
- Branch: `feature/62-m7-performance-ti` (merged #63)
- Target release: **v1.11.0** (released 2026-08-24)
- Created: 2026-08-24
- Last updated: 2026-08-24
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: Captain decisions on Open Questions (see below)
- Rollback checkpoint: `rollback/pre-m7-performance-ti` @ `d05b7b8`
- Feature PR: [#63](https://github.com/loganware05/captains-compass-cursor/pull/63) (merged @ `a71663b`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1–M6 COMPLETE (v1.5.0–v1.10.0)
  - Baseline: **v1.10.0** (`d05b7b8` / current `main` after closeout #61)
  - ADR-022 deferral: performance-knowledge ingest + live TI → M7
- Machine artifacts: `.agent/plans/m7-performance-ti/`

## Request

Proceed with **Milestone 7** of the Captain Compass multi-agent orchestration OS:

1. **Performance-knowledge ingest** — map `ExecutionRun` and `Experience` artifacts
   into durable `kind: performance` knowledge items with execution metrics and
   provenance (explicit CLI only).
2. **Live Technology Intelligence adapter** — opt-in GitHub Stars-shaped discovery
   via `gh` / GitHub API for capability planning, **Captain-gated**, never CI
   default, never auto-execute external repos.

## Problem Statement

After M6:

- `ExecutionRun` ingest maps to `kind: artifact` with minimal metrics; ADR-022
  deferred **performance** knowledge form enrichment to M7
- Experience ingest produces `kind: performance` but lacks structured execution
  metrics (retries, agents/models, capability linkage)
- Plan writer **Knowledge Context** does not surface a dedicated **Performance**
  readback for planners evaluating historical execution quality
- Technology Intelligence is **stub** (CI) or **file** (offline fixtures) only;
  live GitHub Stars discovery is documented but not wired
- The Notion architecture expects Technology Intelligence to answer “what external
  patterns/repos might help?” — currently only offline redacted samples

Without M7, execution telemetry and live discovery remain disconnected from the
unified knowledge layer and planning readback.

## Desired Outcome

After M7 (v1.11.0), Captain Compass can:

1. Ingest **performance knowledge items** from `.agent/runs/` and
   `.agent/experience/` with structured metrics (outcome, retries, skills,
   agents/models, plan/task linkage)
2. Query performance knowledge via existing `query-knowledge.sh --kind performance`
3. Surface **Performance Context** in capability plans (informational; no matcher
   weight changes)
4. Query live TI via explicit opt-in (`COMPASS_TI_PROVIDER=github-stars`) using
   authenticated `gh` when Captain runs planning locally
5. Retain all M5–M6 safety invariants: explicit CLI ingest, NOT APPROVED FOR
   EXECUTION banner, no auto-install of external repos

## Acceptance Criteria

- [x] `item_from_execution_run` maps to `kind: performance` with optional
      `performance_metrics` object (outcome, retries, skills, agents, models,
      plan_id, task_id, experience_id)
- [x] Experience ingest enriches performance items (capabilities exercised,
      lessons, run linkage)
- [x] Schema allows optional `performance_metrics` on knowledge items (backward
      compatible)
- [x] Plan writer **Performance Context** section (top-N `kind: performance`
      from hybrid/keyword query on objective)
- [x] `GithubStarsTechnologyIntelligenceProvider` behind
      `COMPASS_TI_PROVIDER=github-stars` (opt-in only)
- [x] Live TI uses `gh` when available; fails closed to empty list without auth
      (no CI network calls by default)
- [x] Golden-recorded fixtures for live TI mapper tests (no network in CI)
- [x] CLI `./scripts/query-technology-intelligence.sh` for explicit Captain TI
      queries (read-only)
- [x] Extend `knowledge-steward` + `candidate-promotion` Skills; doctor checks
- [x] ADR-023 for performance knowledge + live TI boundaries
- [x] Doctor / install / tests / evals pass
- [x] Control-repo only; sandbox refresh after release

## Non-Goals

- Auto-ingest performance on `record-execution-run.sh` (explicit CLI only)
- Auto-install or execute starred repositories
- Setting `approved_for_execution: true` on TI candidates
- Production embedding / vector DB providers (still deferred)
- Full GitHub Star Categorization pipeline (batch ML) — M7 is **live query adapter**
- NotebookLM / Notion MCP ingestion
- Mutating matcher weights from performance or TI readback

## Assumptions

- M5/M6 knowledge store, hybrid query, and ingest audit remain stable
- Captain has `gh auth login` for local live TI demos (optional)
- CI continues on `COMPASS_TI_PROVIDER=stub` with golden fixtures for github-stars mapper
- Performance items use idempotent keys (`know-run-*`, `know-exp-*`)

## Open Questions (Captain — resolved 2026-08-24)

1. **Live TI scope:** GitHub **starred repos only** (`COMPASS_TI_PROVIDER=github-stars`).
2. **Performance Context default:** **always render** section (empty when none).
3. **Re-ingest execution runs:** **overwrite** existing `know-run-*` as `kind: performance`.
4. **Target version:** **v1.11.0**.
5. **Skills:** **extend** `knowledge-steward` + `candidate-promotion` **and ship**
   `technology-intelligence-live` Skill.

## Current-State Analysis

| Area | State (v1.10.0) |
|---|---|
| ExecutionRun ingest | `kind: artifact`, basic summary |
| Experience ingest | `kind: performance`, basic summary |
| Knowledge query | keyword / vector / hybrid |
| Plan sections | Knowledge Context (hybrid when index exists) |
| TI providers | `stub` (default), `file` (offline fixtures) |
| Live GitHub Stars | Documented only |

## Proposed Architecture

```text
orchestrator/knowledge/ingest.py
  item_from_execution_run()   # EXTEND → kind: performance + metrics
  item_from_experience()      # EXTEND → richer performance fields

orchestrator/schemas/knowledge-item.schema.json
  performance_metrics         # NEW optional object

orchestrator/plan_writer/
  build.py                    # performance_context query
  render.py                   # Performance Context section

orchestrator/providers/technology_intelligence/
  github_stars_provider.py    # NEW live adapter (gh-backed)
  file_provider.py            # shared _candidate_from_stars_shaped mapper
  select_ti_provider()        # EXTEND: github-stars branch

scripts/
  query-technology-intelligence.sh   # NEW explicit TI CLI
  ingest-knowledge.sh                # document runs+experience performance path

tests/fixtures/ti/github-stars-recorded/
tests/orchestrator/test_m7_performance_ti.py
```

**Safety invariants:**

- Live TI never default; CI uses stub + golden recordings
- TI candidates always `approved_for_execution: false`
- Performance ingest explicit CLI only
- Performance / TI sections informational only in plans

## Required Capabilities

Inferred from the objective and repository context.

- performance-metrics-ingest
- execution-run-knowledge-mapping
- experience-performance-enrichment
- plan-performance-context-section
- github-stars-ti-adapter
- ti-golden-record-testing
- captain-gated-live-discovery
- explicit-cli-ti-query

**Domains detected:** knowledge, github, plan

Human intent also requires: gh auth boundary, fail-closed without credentials,
extend existing Knowledge Steward workflow.

## Reusable Capabilities Found

Approved Compass Skills ranked for this objective (deterministic matcher).

| Skill | Score | Notes |
|---|---:|---|
| `knowledge-steward` | 0.5571 | performance ingest + query |
| `execution-telemetry` | 0.4929 | ExecutionRun / Experience sources |
| `candidate-promotion` | 0.4286 | TI candidate ceiling |
| `github-integration` | 0.3643 | gh CLI for live TI |
| `capability-planning` | 0.3643 | plan writer integration |
| `compass-evaluator` | 0.3 | evaluation artifacts |
| `experience-routing` | 0.3 | routing context |
| `testing-validation` | 0.3 | validation evidence |
| `security-review` | 0.3 | TI boundary review |

Prefer in implementation manifests: `knowledge-steward`, `execution-telemetry`,
`candidate-promotion`, `github-integration`, `capability-planning`.

### Capability Gaps

No new Skill required unless Captain requests `technology-intelligence-live`;
default proposal extends existing Skills.

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only.

*No external candidates queried (Technology Intelligence provider: stub).*

## Experience Signals

Informational readback from Experience fixtures/stores. **Does not auto-adjust matcher weights** (proposal-only via Skill `experience-routing`).

| Experience | Outcome | Skills |
|---|---|---|
| `exp-fixture-contact-counter` | success | `react-engineering`, `testing-validation`, `accessibility-review`, `capability-planning` |
| `exp-db7b997bc1a4` | success | `compass-evaluator`, `experience-routing`, `candidate-promotion`, `execution-telemetry`, `implementation-planning` |

## Knowledge Context

Informational readback from `.agent/knowledge/` (hybrid search when vector index exists). **Does not alter Skill rankings or matcher weights.**

| Item | Kind | Score | Title |
|---|---|---:|---|
| `know-adr-022` | decision | 0.5484 | ADR-022: TF-IDF vector Experience store with hybrid knowledge search (v1.10.0 M6) |
| `know-adr-018` | decision | 0.3226 | ADR-018: Execution telemetry, file TI, and Experience dual-path (v1.6.0 M2) |
| `know-adr-021` | decision | 0.2581 | ADR-021: Knowledge Steward with stdlib keyword index (v1.9.0 M5) |

## Task Graph

**Human-authored M7 phases:**

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| T-A | `performance_metrics` schema + ingest mappers (runs, experience) | — | no |
| T-B | Plan writer **Performance Context** section | T-A | yes (vs T-C) |
| T-C | `GithubStarsTechnologyIntelligenceProvider` + golden recordings | — | yes (vs T-B) |
| T-D | `query-technology-intelligence.sh`; extend Skills; doctor/install | T-A, T-C | no |
| T-E | Tests/evals; ADR-023; docs | T-B–T-D | no |
| T-F | Release prep v1.11.0 | T-E | no |

Generic planner artifact: `.agent/plans/m7-performance-ti/task-graph.json`

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| Discovery / architecture | `repository-scout` / `architecture-agent` | `capability-planning`, `implementation-planning` |
| Performance ingest | `implementation-agent` | `knowledge-steward`, `execution-telemetry` |
| Live TI adapter | `implementation-agent` | `github-integration`, `candidate-promotion`, `security-review` |
| Plan integration | `implementation-agent` | `capability-planning`, `knowledge-steward` |
| Validation | `test-engineer` | `testing-validation`, `security-review` |
| Documentation | `documentation-agent` | `pull-request-preparation`, `candidate-promotion` |

Machine manifests: `.agent/plans/m7-performance-ti/manifests.json`

## Workstreams

1. **Performance knowledge mappers** — runs/experience → `kind: performance`
2. **Performance Context** — plan section (informational)
3. **Live TI adapter** — github-stars via gh, golden CI tests
4. **CLIs + Skills** — query TI, extend knowledge-steward
5. **Harness** — ADR-023, doctor, tests, release

## Parallelization Plan

T-A and T-C can start in parallel. T-B depends on T-A. T-D integrates T-A+T-C.
T-E integrates all. Avoid parallel edits on `orchestrator/plan_writer/`.

## Files Expected to Change

### New

```text
orchestrator/providers/technology_intelligence/github_stars_provider.py
orchestrator/providers/technology_intelligence/mapper.py
scripts/query-technology-intelligence.sh
tests/fixtures/ti/github-stars-recorded/
tests/fixtures/knowledge/performance/
tests/orchestrator/test_m7_performance_ti.py
```

### Modified

```text
orchestrator/knowledge/ingest.py
orchestrator/schemas/knowledge-item.schema.json
orchestrator/plan_writer/build.py
orchestrator/plan_writer/render.py
orchestrator/providers/technology_intelligence/file_provider.py
orchestrator/providers/technology_intelligence/__init__.py
.cursor/skills/knowledge-steward/SKILL.md
.cursor/skills/candidate-promotion/SKILL.md
scripts/doctor.sh
scripts/ingest-knowledge.sh
tests/evals/run.sh
tests/orchestrator/test_m5_knowledge_steward.py
docs/integrations/technology-intelligence.md
DECISIONS.md
TESTING.md
README.md
PROJECT_CONTEXT.md
CHANGELOG.md (on release)
VERSION (on release)
```

## Testing Strategy

Evidence under `.agent/evidence/m7-performance-ti/`.

| Layer | Action |
|---|---|
| Unit | execution-run → performance item with metrics |
| Unit | experience enrich preserves idempotency |
| Unit | github-stars mapper from golden recordings (no network) |
| Unit | live provider returns [] without gh auth |
| Integration | ingest runs+experience → query `--kind performance` |
| Integration | capability plan renders Performance Context |
| Integration | `COMPASS_TI_PROVIDER=github-stars` with mock gh stdout |
| Evals | CI stays stub; golden TI isolation sensors |
| Security | TI never sets approved_for_execution; no secret paths in ingest |
| Rollback | tag restores artifact-kind runs + stub-only TI |

## Security Review

- Live TI requires explicit env + gh auth; no tokens in repo
- TI output validated; fail closed on schema violations
- Performance ingest rejects secret paths (existing M5 guards)
- No external repo code import at planning time

## Accessibility Review

Not applicable (no UI).

## Migration Plan

1. Product repos: `update.sh` adds docs/CLI; no behavior change until Captain runs ingest/TI
2. Re-ingest updates `know-run-*` items to `kind: performance` (idempotent)
3. CI unchanged on stub TI default

## Deployment Plan

- Merge via PR after validation
- Tag `v1.11.0`
- Sandbox `update.sh` + optional performance ingest + TI demo (local gh)

## Rollback Plan

1. Restore `rollback/pre-m7-performance-ti`
2. Revert VERSION to 1.10.0
3. Remove performance_metrics from re-ingested items if needed (re-run ingest)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Live TI flakiness / rate limits | Broken local demos | Fail closed; golden recordings; cache optional later |
| gh not installed | Empty TI results | Clear CLI error message; document prerequisites |
| Performance item noise | Bad planning context | `--kind performance` filter; top-N cap |
| CI network leakage | Nondeterministic tests | Stub default; mock gh in tests only |
| Scope creep to full Stars ML | Delay M7 | Adapter boundary; redacted mapping only |

## Evaluation Strategy

After implementation (post-approval), success by:

- Acceptance criteria checked
- Doctor / tests / evals green
- Stub CI identical to v1.10.0 for default env
- Fixture ingest → Performance Context populated
- Live TI with mocked gh returns validated candidates

## Learning Plan

Retain under `.agent/plans/m7-performance-ti/`:

- `resolve.json`, `task-graph.json`, `manifests.json`
- Link issue, branch, PR, evidence after execution

Feeds M8+ optional TI cache, broader discovery providers after Captain expands scope.

## Autonomy Budget

After approval, create `.agent/budgets/m7-performance-ti.md`.

- Maximum iterations: 20
- Maximum failed validation cycles: 5
- Maximum estimated cost: Captain-defined
- Maximum elapsed time: 5 working days
- Maximum live TI query batches per plan: 10 (M7-specific)
- Budget ledger path: `.agent/budgets/m7-performance-ti.md`

## Definition of Done

- All Acceptance Criteria checked
- Doctor / tests / evals green
- Security review recorded
- ADR-023 accepted
- PROGRESS / CHANGELOG / TESTING updated
- PR prepared with evidence
- No implementation on protected branches

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Machine-generated capability matches and agent manifests are **proposals** only.
The Captain may approve, revise, or reject before any product implementation
proceeds.

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-24
- **Approved revision:** starred repos only; Performance Context always render; re-ingest overwrite; v1.11.0; extend Skills + technology-intelligence-live
- **Issue:** #62
- **Branch:** feature/62-m7-performance-ti
- **Rollback:** rollback/pre-m7-performance-ti @ d05b7b8
- **Feature PR:** #63 (merged)
- **Release:** v1.11.0 (2026-08-24)
