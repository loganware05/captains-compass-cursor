# Implementation Plan

## Metadata

- Status: APPROVED
- Plan ID: m5-knowledge-steward
- Issue: [#54](https://github.com/loganware05/captains-compass-cursor/issues/54)
- Branch: `feature/54-m5-knowledge-steward`
- Target release: **v1.9.0** (additive; non-breaking)
- Created: 2026-08-24
- Last updated: 2026-08-24
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: post-approval decisions recorded below
- Rollback checkpoint: `rollback/pre-m5-knowledge-steward` @ `56bb5bc`
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1–M4 COMPLETE (v1.5.0–v1.8.0)
  - Baseline: **v1.8.0** (`56bb5bc` / current `main` after closeout #53)
- Machine artifacts: `.agent/plans/m5-knowledge-steward/`

## Request

Proceed with **Milestone 5** of the Captain Compass multi-agent orchestration OS:
deliver the **Knowledge Steward** leadership role and `orchestrator/knowledge/` slice —
curate Experiences, evaluations, routing artifacts, and project memory into a
**searchable, provenance-rich knowledge store** that informs planning without
weakening the approval gate or requiring a live vector database in CI.

## Problem Statement

After M4:

- Learning artifacts are scattered: `.agent/experience/`, `.agent/evaluations/`,
  `.agent/routing/`, proficiency/promotion metadata, and markdown memory docs
  (`DECISIONS.md`, `PROGRESS.md`) are not unified or queryable
- The Notion architecture defines five knowledge forms (Knowledge, Decisions,
  Procedures, Performance, Artifacts) and a **Knowledge Steward** role — neither
  is implemented
- Plan writer surfaces **Experience Signals** only; no consolidated **Knowledge
  Context** for planners
- Procedure promotion from successful Experiences remains ad hoc (Skill training
  sidecar path only)
- No retention, confidence, or provenance model for durable learned items

Without M5, Compass cannot answer “what does this project already know?” during
planning in a structured, auditable way.

## Desired Outcome

After M5 (v1.9.0), Captain Compass can:

1. **Ingest** schema-valid knowledge items from existing artifacts (Experiences,
   evaluations, routing proposals, execution runs, optional ADR excerpts) into
   `.agent/knowledge/items/` with provenance links
2. **Index** items with a stdlib-first keyword index (deterministic; rebuildable)
   — no vector DB required in CI
3. **Query** via CLI + Skill `knowledge-steward` for planning context (top-N
   matches with provenance; read-only by default)
4. Render a **Knowledge Context** section in capability plans (informational;
   does not alter Skill rankings or weights)
5. **Propose procedure promotion** from Captain-approved knowledge (staging +
   proposal only — same PR gate pattern as persistent roles)
6. Ship optional **Knowledge Steward subagent** profile for curation tasks
7. Keep product implementation behind the existing approval gate; no live TI;
   no silent Skill/agent installs

## Acceptance Criteria

- [x] Schema `knowledge-item.schema.json` covering Notion knowledge forms:
      `knowledge`, `decision`, `procedure`, `performance`, `artifact`
- [x] `orchestrator/knowledge/` module: ingest, index (keyword), query, retention
      constants; pluggable `VectorIndexAdapter` stub for future M6+ vector store
- [x] Store layout: `.agent/knowledge/items/`, `.agent/knowledge/index.json`,
      `.agent/knowledge/ingest-log/` (audit)
- [x] Skill `knowledge-steward` + CLIs:
      `ingest-knowledge.sh` (explicit paths or `--from-store experience,evaluations`),
      `query-knowledge.sh` (keyword search + `--kind` filter)
- [x] Ingestion is **explicit CLI only**; no auto-run on plan close
- [x] Plan writer **Knowledge Context** section (like Experience Signals;
      informational only)
- [x] Procedure promotion **proposal** schema + staging under
      `.agent/knowledge/procedures/staging/` (Captain PR to land; no auto-merge)
- [x] `.cursor/agents/knowledge-steward.md` subagent
- [x] ADR-021 for Knowledge Steward + stdlib index vs deferred vector store
- [x] Doctor / install / tests / evals pass
- [ ] Control-repo only; sandbox refresh after release

## Non-Goals

- Production vector database (Pinecone, pgvector, etc.) in M5 — adapter interface
  only; default remains keyword index
- Live GitHub Stars / network TI in CI
- Auto-ingest on every workstream close without explicit CLI or Captain flag
- Silent promotion of procedures into `.cursor/skills/` or rules
- Replacing markdown project memory (`DECISIONS.md`, etc.) — Knowledge Steward
  **indexes and links**, does not delete source docs
- Changing plan-approval hook semantics
- Full NotebookLM / Notion MCP ingestion (defer; document extension point)

## Assumptions

- M2–M4 artifact schemas remain stable (`experience`, `evaluation`,
  `routing-proposal`, `execution-run`)
- Python 3 stdlib sufficient for keyword tokenization + inverted index
- Product repos may gitignore `.agent/knowledge/items/` runtime entries; control
  repo ships fixtures + tests
- Captain will review procedure promotion PRs manually

## Resolved Decisions (Captain, 2026-08-24)

1. **Ingestion trigger:** Explicit CLI only — no hooks on workstream close or
   `record-execution-run.sh`.
2. **Subagent:** Ship `.cursor/agents/knowledge-steward.md` in M5.
3. **DECISIONS.md sync:** Auto-ingest ADR headings when ingest CLI processes
   `DECISIONS.md` (via explicit path or `--from-store decisions`).
4. **Target version:** **v1.9.0** confirmed.

## Current-State Analysis

| Area | State (v1.8.0) |
|---|---|
| Experience / runs | `.agent/experience/`, `.agent/runs/` + schemas |
| Evaluations | `.agent/evaluations/` + evaluator Skill/CLI |
| Routing | proposals + applied audit; bounded apply |
| Proficiency / roles | `.agent/agents/proficiency/`, promotions staging |
| Project memory | Markdown docs (not machine-queryable) |
| Plan sections | Experience Signals only |
| `orchestrator/knowledge/` | Not present |

## Proposed Architecture

```text
.agent/knowledge/
  items/              # knowledge-item JSON (gitignored runtime; fixtures in tests)
  index.json          # keyword inverted index (rebuildable)
  ingest-log/         # audit entries per ingest batch
  procedures/
    proposals/        # procedure promotion proposals
    staging/          # draft procedure playbooks

orchestrator/knowledge/
  ingest.py           # map Experience/evaluation/routing/run → knowledge items
  index.py            # build/query keyword index
  query.py            # ranked search with provenance
  promote.py          # procedure promotion proposals (staging only)
  adapters/
    vector.py         # VectorIndexAdapter protocol + NoOp stub

orchestrator/schemas/knowledge-item.schema.json
orchestrator/schemas/procedure-promotion.schema.json

.cursor/skills/knowledge-steward/
.cursor/agents/knowledge-steward.md   # optional per Open Q2

scripts/ingest-knowledge.sh
scripts/query-knowledge.sh
scripts/propose-procedure-from-knowledge.sh
```

**Safety invariants:**

- Knowledge query is read-only for planning; never mutates matcher weights
- Procedure promotion = staging + Captain PR only (same pattern as M4 roles)
- Ingestion never writes secrets; redact paths matching `.env` patterns
- Vector adapter default is NoOp; CI uses keyword index only

## Required Capabilities

Inferred from the objective and repository context.

- knowledge-item-schema
- provenance-tracking
- keyword-index-build
- knowledge-query
- experience-ingestion
- evaluation-ingestion
- procedure-promotion-proposal
- plan-knowledge-context-section
- captain-gated-ingestion

**Domains detected:** plan, github, knowledge

Human intent also requires: stdlib index, audit log, Skill/subagent curation,
integration with existing telemetry and evaluator artifacts.

## Reusable Capabilities Found

Approved Compass Skills ranked for this objective (deterministic matcher).

| Skill | Score | Notes |
|---|---:|---|
| `implementation-planning` | 0.5571 | capability_overlap=0.2571 |
| `github-integration` | 0.4286 | lifecycle_stage=0.15 |
| `pull-request-preparation` | 0.3643 | lifecycle_stage=0.15 |
| `execution-telemetry` | 0.255 | lifecycle_stage=0.105 |
| `compass-evaluator` | 0.255 | lifecycle_stage=0.105 |
| `experience-routing` | 0.255 | lifecycle_stage=0.105 |
| `experience-skill-training` | 0.255 | lifecycle_stage=0.105 |
| `persistent-role-promotion` | 0.255 | lifecycle_stage=0.105 |
| `bounded-autonomy` | 0.255 | lifecycle_stage=0.105 |
| `capability-planning` | 0.3 | lifecycle_stage=0.15 |

Prefer in implementation manifests: `execution-telemetry`, `compass-evaluator`,
`experience-routing`, `experience-skill-training`, `capability-planning`.

### Capability Gaps

No capability gaps detected for the inferred requirements (new Skill
`knowledge-steward` will be authored in M5).

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only.

*No external candidates queried (Technology Intelligence provider: stub).*

## Experience Signals

Informational readback from Experience fixtures/stores. **Does not auto-adjust matcher weights** (proposal-only via Skill `experience-routing`).

| Experience | Outcome | Skills |
|---|---|---|
| `exp-fixture-contact-counter` | success | `react-engineering`, `testing-validation`, `accessibility-review`, `capability-planning` |
| `exp-db7b997bc1a4` | success | `compass-evaluator`, `experience-routing`, `candidate-promotion`, `execution-telemetry`, `implementation-planning` |

## Task Graph

**Human-authored M5 phases:**

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| T-A | `knowledge-item` + `procedure-promotion` schemas; store layout | — | no |
| T-B | Ingest mappers (Experience, evaluation, routing, run) + audit log | T-A | yes (vs T-C) |
| T-C | Keyword index build/query module + `VectorIndexAdapter` stub | T-A | yes (vs T-B) |
| T-D | Skill/CLIs + optional subagent; procedure promotion staging | T-B | no |
| T-E | Plan writer Knowledge Context section; doctor/install/tests/evals; ADR-021 | T-B–T-D | no |
| T-F | Release prep v1.9.0 | T-E | no |

Generic planner artifact: `.agent/plans/m5-knowledge-steward/task-graph.json`

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| Discovery / architecture | `repository-scout` / `architecture-agent` | `capability-planning`, `implementation-planning` |
| Implementation | `implementation-agent` | `execution-telemetry`, `compass-evaluator`, `knowledge-steward` |
| Validation | `test-engineer` | `testing-validation` |
| Security | `security-reviewer` | `security-review` |
| Knowledge curation | `knowledge-steward` (new) | `knowledge-steward`, `experience-routing` |
| Documentation | `documentation-agent` | `pull-request-preparation` |

Machine manifests: `.agent/plans/m5-knowledge-steward/manifests.json`

## Workstreams

1. **Schemas + store layout** — knowledge forms, provenance, retention fields
2. **Ingestion pipeline** — artifact → knowledge item; audit log
3. **Keyword index + query** — deterministic search; vector adapter stub
4. **Knowledge Steward Skill/CLI/subagent** — curation workflow
5. **Procedure promotion proposals** — staging + Captain PR path
6. **Plan integration** — Knowledge Context section
7. **Harness** — ADR-021, doctor, tests, release

## Parallelization Plan

T-A first. T-B and T-C can proceed in parallel after T-A. T-D depends on T-B.
T-E integrates all. Avoid parallel worktrees on `orchestrator/plan_writer/`.

## Files Expected to Change

### New

```text
orchestrator/knowledge/__init__.py
orchestrator/knowledge/ingest.py
orchestrator/knowledge/index.py
orchestrator/knowledge/query.py
orchestrator/knowledge/promote.py
orchestrator/knowledge/adapters/vector.py
orchestrator/schemas/knowledge-item.schema.json
orchestrator/schemas/procedure-promotion.schema.json
.cursor/skills/knowledge-steward/SKILL.md
.cursor/skills/knowledge-steward/capability.yaml
.cursor/agents/knowledge-steward.md
scripts/ingest-knowledge.sh
scripts/query-knowledge.sh
scripts/propose-procedure-from-knowledge.sh
tests/fixtures/knowledge/
tests/orchestrator/test_m5_knowledge_steward.py
.agent/knowledge/.gitkeep
.agent/knowledge/ingest-log/.gitkeep
.agent/knowledge/procedures/.gitkeep
```

### Modified

```text
orchestrator/plan_writer/build.py
orchestrator/plan_writer/render.py
orchestrator/registry/compiler.py
orchestrator/schemas/validate.py
scripts/doctor.sh
scripts/install.sh
tests/evals/run.sh
tests/run.sh
DECISIONS.md
TESTING.md
README.md
PROJECT_CONTEXT.md
CHANGELOG.md (on release)
VERSION (on release)
```

## Testing Strategy

Evidence under `.agent/evidence/m5-knowledge-steward/`.

| Layer | Action |
|---|---|
| Unit | schema validation; ingest maps Experience → knowledge item |
| Unit | keyword index build + query ranking deterministic |
| Unit | query does not mutate weights or registry |
| Unit | procedure promotion rejects without gates; staging only |
| Integration | ingest fixtures → query returns expected items |
| Integration | capability plan renders Knowledge Context section |
| Evals | golden plan determinism unchanged when knowledge store empty |
| Security | path-safe IDs; no secret capture in ingest |
| Rollback | tag restores pre-M5 knowledge module absence |

## Security Review

- Ingest must not copy `.env` or credential paths into knowledge items
- Query results are read-only; no arbitrary file read outside `.agent/knowledge/`
- Procedure promotion staging must not grant elevated permissions

## Accessibility Review

Not applicable (no UI).

## Migration Plan

1. Product repos: `update.sh` adds Skill + optional subagent; empty knowledge store
2. Existing workflows unchanged until Captain runs ingest CLI
3. Forward-only; keyword index rebuildable from items/

## Deployment Plan

- Merge via PR after validation
- Tag `v1.9.0`
- Sandbox `update.sh` + optional ingest/query demo

## Rollback Plan

1. Restore `rollback/pre-m5-knowledge-steward`
2. Revert VERSION to 1.8.0
3. Remove `.agent/knowledge/index.json` if needed (items are additive)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Index drift vs items | Stale query results | Rebuild index command; ingest audit |
| Over-ingestion noise | Bad planning context | Kind filters; retention constants; top-N cap |
| Scope creep to vector DB | CI complexity | Adapter stub only; ADR documents deferral |
| Duplicate knowledge items | Index bloat | Idempotent ingest keys from source artifact IDs |

## Evaluation Strategy

After implementation (post-approval), success by:

- Acceptance criteria checked
- Doctor / tests / evals green
- Empty knowledge store → plans identical to v1.8.0 (except new section header absent or “none”)
- Ingest fixtures → query returns provenance-linked items
- Procedure promotion never writes `.cursor/skills/` directly

## Learning Plan

Retain under `.agent/plans/m5-knowledge-steward/`:

- `resolve.json`, `task-graph.json`, `manifests.json`
- Link issue, branch, PR, evidence after execution

Feeds M6+ vector Experience store and live TI only after Captain expands scope.

## Autonomy Budget

After approval, create `.agent/budgets/m5-knowledge-steward.md`.

- Maximum iterations: 20
- Maximum failed validation cycles: 5
- Maximum estimated cost: Captain-defined
- Maximum elapsed time: 5 working days
- Maximum ingest batches per plan: 10 (M5-specific)
- Budget ledger path: `.agent/budgets/m5-knowledge-steward.md`

## Definition of Done

- All Acceptance Criteria checked
- Doctor / tests / evals green
- Security review recorded
- ADR-021 accepted
- PROGRESS / CHANGELOG / TESTING updated
- PR prepared with evidence
- No implementation on protected branches

## Approval Boundary

Plan is **APPROVED**. Implementation proceeds on `feature/54-m5-knowledge-steward`
only — never on protected base branches.

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-24
- **Approved revision:** Explicit CLI ingest; knowledge-steward subagent; auto-ingest ADR headings; v1.9.0
- **Issue:** [#54](https://github.com/loganware05/captains-compass-cursor/issues/54)
- **Branch:** `feature/54-m5-knowledge-steward`
- **Rollback:** `rollback/pre-m5-knowledge-steward` @ `56bb5bc`
