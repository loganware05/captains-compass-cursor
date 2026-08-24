# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m6-vector-experience-store
- Issue: [#58](https://github.com/loganware05/captains-compass-cursor/issues/58)
- Branch: `feature/58-m6-vector-experience-store` (merged #59)
- Target release: **v1.10.0** (released 2026-08-24)
- Created: 2026-08-24
- Last updated: 2026-08-24
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: hybrid plan-writer default; dedicated rebuild script; performance ingest M7
- Rollback checkpoint: `rollback/pre-m6-vector-experience-store` @ `abbb316`
- Feature PR: [#59](https://github.com/loganware05/captains-compass-cursor/pull/59) (merged @ `3859000`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1–M5 COMPLETE (v1.5.0–v1.9.0)
  - Baseline: **v1.9.0** (`6f09555` / current `main` after closeout #57)
  - ADR-021 deferral: production vector DB → M6+
- Machine artifacts: `.agent/plans/m6-vector-experience-store/`

## Request

Proceed with **Milestone 6** of the Captain Compass multi-agent orchestration OS:
deliver a **local Vector Experience Store** — a CI-safe, file-backed semantic index
that extends M5 Knowledge Steward with hybrid keyword + vector search, without
production vector databases, live Technology Intelligence, or weakening the
approval gate.

## Problem Statement

After M5:

- Knowledge query is **keyword-only**; semantically related items with low token
  overlap are missed (e.g. “routing weights” vs “matcher tuning”)
- `VectorIndexAdapter` is a **NoOp stub**; ADR-021 explicitly deferred vector
  search to M6+
- Plan writer **Knowledge Context** uses keyword query only; no semantic recall
- The Notion architecture expects durable learning artifacts to inform planning
  beyond exact token matches
- `PROJECT_CONTEXT.md` lists **vector Experience store adapter** as remaining
  technical debt

Without M6, Knowledge Steward recall quality plateaus at keyword overlap while
the architecture promises richer Experience-driven intelligence.

## Desired Outcome

After M6 (v1.10.0), Captain Compass can:

1. Build a **rebuildable file-backed vector index** from `.agent/knowledge/items/`
   using stdlib TF-IDF + cosine similarity (no external embedding API in CI)
2. Query knowledge in **`keyword`**, **`vector`**, or **`hybrid`** modes via
   explicit CLI (`query-knowledge.sh --mode hybrid`)
3. Optionally rebuild vector index during explicit ingest
   (`ingest-knowledge.sh --rebuild-vector`)
4. Surface **hybrid-ranked Knowledge Context** in capability plans when a vector
   index exists (informational only — no matcher weight changes)
5. Retain M5 safety invariants: explicit CLI only, read-only query, staging-only
   procedure promotion, no secret ingest

## Acceptance Criteria

- [x] `FileVectorIndexAdapter` implements `VectorIndexAdapter` with TF-IDF sparse
      vectors stored under `.agent/knowledge/vector-index.json`
- [x] `query_knowledge()` supports `mode=keyword|vector|hybrid`; default remains
      **`keyword`** for backward compatibility
- [x] Hybrid merge is deterministic, documented, and includes provenance +
      per-mode scores on results
- [x] Vector index rebuild is **explicit CLI only** (ingest flag or dedicated
      rebuild script); no hooks
- [x] Empty or missing vector index → vector/hybrid modes degrade gracefully to
      keyword-only results
- [x] Plan writer Knowledge Context uses hybrid query when vector index exists
      (env override: `COMPASS_KNOWLEDGE_SEARCH_MODE`)
- [x] Extend Skill `knowledge-steward` + doctor checks for vector index layout
- [x] ADR-022 for stdlib TF-IDF vector index vs deferred production embedding DB
- [x] Doctor / install / tests / evals pass
- [ ] Control-repo only; sandbox refresh after release

## Non-Goals

- Production vector databases (Pinecone, pgvector, Weaviate, etc.) in M6
- OpenAI / Hugging Face / network embedding APIs in CI default path
- Live GitHub Stars / network Technology Intelligence (defer **M7+**)
- Auto-ingest or auto-rebuild on workstream close
- Changing plan-approval hook semantics or matcher weight mutation from query
- Replacing keyword index (both indexes coexist; keyword remains rebuildable)
- Performance-knowledge ingest mappers (defer unless Captain expands scope in
  approval revision)
- NotebookLM / Notion MCP ingestion

## Assumptions

- M5 knowledge item schema and ingest paths remain stable
- Python 3 stdlib (`math`, `json`, `re`) sufficient for TF-IDF + cosine similarity
- Vector index size stays small enough for file JSON in control-repo tests/fixtures
- Captain continues explicit CLI ingestion workflow from M5
- Product repos may gitignore runtime vector index; control repo ships fixtures

## Resolved Decisions (Captain, 2026-08-24)

1. **Plan-writer default** when vector index exists: **hybrid** Knowledge Context.
2. **Rebuild CLI:** `ingest-knowledge.sh --rebuild-vector` **and**
   `rebuild-knowledge-vector-index.sh`.
3. **Target version:** **v1.10.0** confirmed.
4. **Performance ingest:** defer to **M7**.

## Open Questions (Captain — resolve at approval)

_Resolved — see above._

## Current-State Analysis

| Area | State (v1.9.0) |
|---|---|
| Knowledge items | `.agent/knowledge/items/` + ingest CLI |
| Keyword index | `.agent/knowledge/index.json` (TF token overlap) |
| Vector adapter | `NoOpVectorIndexAdapter` only |
| Query CLI | `--query`, `--kind`, `--top` (keyword only) |
| Plan Knowledge Context | Keyword query via `build.py` |
| Experience / TI / routing | M2–M4 unchanged |

## Proposed Architecture

```text
.agent/knowledge/
  items/              # existing knowledge-item JSON
  index.json          # existing keyword inverted index
  vector-index.json   # NEW: TF-IDF sparse vectors + corpus stats
  ingest-log/         # existing audit

orchestrator/knowledge/
  index.py            # existing keyword index (unchanged contract)
  query.py            # EXTEND: mode keyword|vector|hybrid merge
  vector_index.py     # NEW: build/load TF-IDF vectors, cosine scoring
  adapters/
    vector.py         # EXTEND: FileVectorIndexAdapter + NoOp default

scripts/
  query-knowledge.sh  # EXTEND: --mode keyword|vector|hybrid
  ingest-knowledge.sh # EXTEND: --rebuild-vector (optional)
  rebuild-knowledge-vector-index.sh  # NEW (if Open Q2 = both)

orchestrator/schemas/vector-index.schema.json  # NEW (optional validation)
```

**Hybrid scoring (deterministic proposal):**

```text
final_score = 0.5 * keyword_score + 0.5 * vector_score   # when both present
```

Tie-break: higher keyword score, then `item_id` lexicographic (same as M5).

**Safety invariants (carry forward from M5):**

- Query is read-only; never mutates matcher weights or registry
- Vector rebuild requires explicit CLI
- No secret paths in index build
- Production embedding providers remain behind future adapter interface

## Required Capabilities

Inferred from the objective and repository context.

- tf-idf-vector-build
- cosine-similarity-query
- hybrid-knowledge-ranking
- vector-index-persistence
- knowledge-steward-extension
- explicit-cli-rebuild
- provenance-preservation
- backward-compatible-keyword-default

**Domains detected:** knowledge, plan

Human intent also requires: stdlib-only CI default, deterministic hybrid merge,
integration with existing Knowledge Context section.

## Reusable Capabilities Found

Approved Compass Skills ranked for this objective (deterministic matcher).

| Skill | Score | Notes |
|---|---:|---|
| `knowledge-steward` | 0.5571 | primary M5 Skill to extend |
| `implementation-planning` | 0.4286 | lifecycle_stage=0.15 |
| `capability-planning` | 0.3643 | plan writer integration |
| `execution-telemetry` | 0.3 | Experience source artifacts |
| `compass-evaluator` | 0.3 | evaluation artifact sources |
| `experience-routing` | 0.3 | routing artifact sources |
| `testing-validation` | 0.3 | validation evidence |
| `security-review` | 0.3 | ingest path safety |
| `pull-request-preparation` | 0.3 | release closeout |

Prefer in implementation manifests: `knowledge-steward`, `execution-telemetry`,
`compass-evaluator`, `capability-planning`, `testing-validation`.

### Capability Gaps

No new Skill required unless Captain requests a separate `vector-knowledge` Skill;
**extend `knowledge-steward`** is the default proposal.

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

Informational readback from `.agent/knowledge/` (keyword index). **Does not alter Skill rankings or matcher weights.** Populate via explicit `./scripts/ingest-knowledge.sh`.

| Item | Kind | Score | Title |
|---|---|---:|---|
| `know-adr-021` | decision | 0.5484 | ADR-021: Knowledge Steward with stdlib keyword index (v1.9.0 M5) |
| `know-adr-018` | decision | 0.3226 | ADR-018: Execution telemetry, file TI, and Experience dual-path (v1.6.0 M2) |
| `know-adr-020` | decision | 0.2581 | ADR-020: Persistent-role promotion and bounded Level 3 weight apply (v1.8.0 M4) |
| `know-adr-019` | decision | 0.1935 | ADR-019: Evaluator, experience routing proposals, and dual promotion ceilings (v1.7.0 M3) |
| `know-adr-014` | decision | 0.1613 | ADR-014: Critical hooks are fail-closed; autonomy budgets are ledger-backed (v1.2.0) |

## Task Graph

**Human-authored M6 phases:**

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| T-A | `vector-index.schema.json` + `vector_index.py` + store paths | — | no |
| T-B | `FileVectorIndexAdapter`; build/rebuild from knowledge items | T-A | yes (vs T-C) |
| T-C | Hybrid query merge in `query.py`; CLI `--mode` | T-A | yes (vs T-B) |
| T-D | Extend `knowledge-steward` Skill; ingest `--rebuild-vector`; doctor/install | T-B | no |
| T-E | Plan writer hybrid Knowledge Context; tests/evals; ADR-022 | T-B–T-D | no |
| T-F | Release prep v1.10.0 | T-E | no |

Generic planner artifact: `.agent/plans/m6-vector-experience-store/task-graph.json`

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| Discovery / architecture | `repository-scout` / `architecture-agent` | `capability-planning`, `implementation-planning` |
| Vector index implementation | `implementation-agent` | `knowledge-steward`, `python-ml`, `code-structure-cleanup` |
| Query / CLI integration | `implementation-agent` | `knowledge-steward`, `testing-validation` |
| Validation | `test-engineer` | `testing-validation`, `compass-evaluator` |
| Security | `security-reviewer` | `security-review` |
| Documentation | `documentation-agent` | `pull-request-preparation`, `knowledge-steward` |

Machine manifests: `.agent/plans/m6-vector-experience-store/manifests.json`

## Workstreams

1. **Vector index module** — TF-IDF build, sparse storage, cosine query
2. **Adapter implementation** — replace NoOp default in explicit vector paths only
3. **Hybrid query** — merge keyword + vector scores deterministically
4. **CLI + Skill extension** — rebuild and query modes
5. **Plan integration** — optional hybrid Knowledge Context
6. **Harness** — ADR-022, doctor, tests, release

## Parallelization Plan

T-A first. T-B and T-C can proceed in parallel after T-A. T-D depends on T-B.
T-E integrates all. Avoid parallel worktrees on `orchestrator/knowledge/query.py`.

## Files Expected to Change

### New

```text
orchestrator/knowledge/vector_index.py
orchestrator/schemas/vector-index.schema.json
scripts/rebuild-knowledge-vector-index.sh          # if Open Q2 = dedicated script
tests/fixtures/knowledge/vector-hybrid/
tests/orchestrator/test_m6_vector_experience_store.py
.agent/knowledge/vector-index.json                 # test fixture only (optional committed sample)
```

### Modified

```text
orchestrator/knowledge/adapters/vector.py
orchestrator/knowledge/query.py
orchestrator/knowledge/ingest.py                    # optional --rebuild-vector hook
orchestrator/knowledge/store.py                     # vector index path helper
orchestrator/plan_writer/build.py
orchestrator/plan_writer/render.py                  # note hybrid mode in section header
orchestrator/schemas/validate.py
.cursor/skills/knowledge-steward/SKILL.md
scripts/query-knowledge.sh
scripts/ingest-knowledge.sh
scripts/doctor.sh
scripts/install.sh
tests/evals/run.sh
tests/orchestrator/test_m5_knowledge_steward.py     # ensure keyword default unchanged
DECISIONS.md
TESTING.md
README.md
PROJECT_CONTEXT.md
CHANGELOG.md (on release)
VERSION (on release)
```

## Testing Strategy

Evidence under `.agent/evidence/m6-vector-experience-store/`.

| Layer | Action |
|---|---|
| Unit | TF-IDF build deterministic on fixtures |
| Unit | cosine scoring ranks semantically closer items higher |
| Unit | hybrid merge deterministic; tie-break stable |
| Unit | missing vector index → vector/hybrid fall back to keyword |
| Unit | query does not mutate weights, registry, or keyword index |
| Integration | ingest fixtures → rebuild vector → hybrid query finds ADR items |
| Integration | capability plan Knowledge Context uses hybrid when index present |
| Evals | golden plan determinism when vector index absent (unchanged from v1.9.0) |
| Security | vector build rejects secret paths; no arbitrary file read |
| Rollback | tag restores NoOp adapter behavior |

## Security Review

- Vector index build must use same secret-path rejection as ingest
- Query remains confined to `.agent/knowledge/` artifacts
- No network calls in default CI vector path
- Hybrid scores are informational only in plans

## Accessibility Review

Not applicable (no UI).

## Migration Plan

1. Product repos: `update.sh` adds vector index path seed; empty until Captain runs rebuild CLI
2. Existing keyword workflows unchanged (`--mode` default `keyword`)
3. Forward-only; vector index rebuildable from items/

## Deployment Plan

- Merge via PR after validation
- Tag `v1.10.0`
- Sandbox `update.sh` + optional hybrid query demo

## Rollback Plan

1. Restore `rollback/pre-m6-vector-experience-store`
2. Revert VERSION to 1.9.0
3. Delete `.agent/knowledge/vector-index.json` if needed (keyword index unaffected)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| TF-IDF quality vs embeddings | Weaker semantic recall | Document limits in ADR-022; hybrid keeps keyword signal |
| Index size growth | Slow rebuild/query | Sparse vectors; retention constants from M5 |
| Non-deterministic float drift | Flaky tests | Round scores; fixed fixture corpus |
| Scope creep to embedding APIs | CI/network deps | Adapter boundary; stdlib-only default |
| Breaking M5 keyword default | Regressions | Default `--mode keyword`; eval golden fixtures |

## Evaluation Strategy

After implementation (post-approval), success by:

- Acceptance criteria checked
- Doctor / tests / evals green
- Missing vector index → behavior identical to v1.9.0 for keyword mode
- Fixture corpus → hybrid returns items keyword-only misses
- No matcher weight or registry mutation from query

## Learning Plan

Retain under `.agent/plans/m6-vector-experience-store/`:

- `resolve.json`, `task-graph.json`, `manifests.json`
- Link issue, branch, PR, evidence after execution

Feeds M7+ live Technology Intelligence adapters and optional embedding
providers only after Captain expands scope.

## Autonomy Budget

After approval, create `.agent/budgets/m6-vector-experience-store.md`.

- Maximum iterations: 20
- Maximum failed validation cycles: 5
- Maximum estimated cost: Captain-defined
- Maximum elapsed time: 5 working days
- Maximum vector rebuild batches per plan: 10 (M6-specific)
- Budget ledger path: `.agent/budgets/m6-vector-experience-store.md`

## Definition of Done

- All Acceptance Criteria checked
- Doctor / tests / evals green
- Security review recorded
- ADR-022 accepted
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
- **Approved revision:** hybrid plan-writer; dedicated rebuild script; v1.10.0; performance ingest M7
- **Issue:** [#58](https://github.com/loganware05/captains-compass-cursor/issues/58)
- **Branch:** `feature/58-m6-vector-experience-store`
- **Rollback:** `rollback/pre-m6-vector-experience-store` @ `abbb316`
