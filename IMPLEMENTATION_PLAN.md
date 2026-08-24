# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m8-procedure-ti-cache
- Issue: [#66](https://github.com/loganware05/captains-compass-cursor/issues/66) — M8: Procedure knowledge lifecycle + offline TI cache (v1.12.0)
- Branch: `feature/66-m8-procedure-ti-cache` (merged #67)
- Target release: **v1.12.0** (released 2026-08-24)
- Created: 2026-08-24
- Last updated: 2026-08-24
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: Procedure Context always render; separate github-stars-cached; staging+approved ingest; v1.12.0; procedure-playbooks Skill
- Rollback checkpoint: `rollback/pre-m8-procedure-ti-cache` @ `c0f02b1`
- Feature PR: [#67](https://github.com/loganware05/captains-compass-cursor/pull/67) (merged @ `ab1efb1`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1–M7 COMPLETE (v1.5.0–v1.11.0)
  - Baseline: **v1.11.0** (`c0f02b1` / current `main` after closeout #65)
  - M7 deferral: optional TI cache → M8; procedure knowledge form incomplete after M5 staging-only promotion
- Machine artifacts: `.agent/plans/m8-procedure-ti-cache/`

## Request

Proceed with **Milestone 8** of the Captain Compass multi-agent orchestration OS:

1. **Procedure knowledge lifecycle** — ingest Captain-approved staging playbooks into
   durable `kind: procedure` knowledge items; surface **Procedure Context** in
   capability plans (informational; explicit CLI only).
2. **Offline TI cache** — explicit file cache for starred-repo discovery signals so
   local planning can reuse last-known TI results without repeated `gh` calls; CI
   remains stub + golden fixtures.

## Problem Statement

After M7:

- M5 shipped procedure **promotion proposals** (staging + PR only) but staging
  playbooks under `.agent/knowledge/procedures/staging/` are **not ingested** as
  queryable `kind: procedure` knowledge items
- Plan writer surfaces Knowledge, Performance, and Experience readback but not
  **Procedure Context** — the third Notion knowledge form remains planning-invisible
- Live TI (`COMPASS_TI_PROVIDER=github-stars`) re-fetches via `gh` on every plan;
  M7 noted **optional TI cache** for M8+ to reduce flakiness and rate-limit risk
- Production embedding APIs remain correctly deferred; M8 should stay stdlib/CI-safe

Without M8, validated playbooks stay orphaned in staging and live TI lacks an offline
reuse path after an explicit Captain refresh.

## Desired Outcome

After M8 (v1.12.0), Captain Compass can:

1. Ingest staging procedure playbooks (`.agent/knowledge/procedures/staging/*/playbook.md`)
   into `kind: procedure` knowledge items with provenance links to source proposals
2. Query procedure knowledge via `query-knowledge.sh --kind procedure`
3. Surface **Procedure Context** in capability plans (always rendered; empty when none)
4. Refresh offline TI cache via explicit CLI (`refresh-ti-cache.sh`) when `gh` auth is available
5. Use cached starred-repo records when `COMPASS_TI_PROVIDER=github-stars-cached` or when
   live provider is configured to prefer cache (Captain decision at approval)
6. Retain all M5–M7 safety invariants: explicit CLI, NOT APPROVED FOR EXECUTION,
   no auto-install of procedures or external repos

## Acceptance Criteria

- [x] `item_from_procedure_playbook()` maps staging playbooks → `kind: procedure`
- [x] `ingest-knowledge.sh --from-store procedures` ingests staging + approved playbooks
      (explicit CLI; never auto on promotion write)
- [x] Plan writer **Procedure Context** section (top-N `kind: procedure` query on objective;
      always rendered; empty when none)
- [x] Offline TI cache at `.agent/intelligence/ti-cache/starred-repos.json` with schema validation
- [x] `./scripts/refresh-ti-cache.sh` — explicit Captain refresh via `gh` (fail closed without auth)
- [x] `CachedGithubStarsTechnologyIntelligenceProvider` behind
      `COMPASS_TI_PROVIDER=github-stars-cached` (opt-in; CI default unchanged)
- [x] Golden-recorded cache fixtures for mapper tests (no network in CI)
- [x] Extend `knowledge-steward` + `technology-intelligence-live` Skills; doctor checks (34 Skills)
- [x] ADR-024 for procedure ingest + TI cache boundaries
- [x] Doctor / install / tests / evals pass
- [ ] Control-repo only; sandbox refresh after release (closeout PR)

## Non-Goals

- Auto-ingest procedures when `propose-procedure-from-knowledge.sh` writes staging
- Auto-install staging playbooks into `.cursor/skills/` or rules
- Production embedding / vector DB providers (still deferred)
- Notion MCP / NotebookLM knowledge ingestion (still deferred)
- Broader TI providers (topic search, Hugging Face, package registries)
- Mutating matcher weights from procedure or cached TI readback
- TTL-based background cache refresh

## Assumptions

- M5–M7 knowledge store, hybrid query, live Stars TI, and procedure promotion staging remain stable
- Captain runs `refresh-ti-cache.sh` locally when they want fresh starred-repo signals cached
- CI continues on `COMPASS_TI_PROVIDER=stub` with golden cache fixtures for cached provider tests
- Procedure items use idempotent keys (`know-proc-<slug>`)

## Open Questions (Captain — resolved 2026-08-24)

1. **Procedure Context default:** **always render** (empty when none).
2. **TI cache provider:** **separate** `github-stars-cached` provider.
3. **Procedure ingest scope:** **staging + approved** roots.
4. **Target version:** **v1.12.0**.
5. **Skills:** **new** dedicated `procedure-playbooks` Skill.

## Current-State Analysis

| Area | State (v1.11.0) |
|---|---|
| Procedure promotion | Staging + proposal JSON only (M5) |
| Procedure ingest | Not implemented |
| Plan sections | Knowledge, Performance, Experience; no Procedure |
| Live TI | `github-stars` via `gh`; no file cache |
| TI cache | Documented deferral from M7 only |
| Skill count | 33 |

## Proposed Architecture

```text
orchestrator/knowledge/ingest.py
  item_from_procedure_playbook()   # NEW → kind: procedure
  STORE_ROOTS["procedures"]        # NEW staging root

orchestrator/plan_writer/
  build.py                         # procedure_context query
  render.py                        # Procedure Context section

orchestrator/providers/technology_intelligence/
  ti_cache.py                      # NEW read/write cache helpers
  github_stars_provider.py         # EXTEND optional cache read path
  file_provider.py                 # select_ti_provider() github-stars-cached branch

scripts/
  refresh-ti-cache.sh              # NEW explicit cache refresh CLI
  ingest-knowledge.sh              # document --from-store procedures

.agent/intelligence/ti-cache/
  starred-repos.json               # runtime cache (gitignored pattern TBD)

tests/fixtures/ti/cache-recorded/
tests/orchestrator/test_m8_procedure_ti_cache.py
```

**Safety invariants:**

- Cache refresh explicit CLI only; never CI network by default
- Cached TI candidates still `approved_for_execution: false`
- Procedure ingest explicit CLI only; staging never auto-promotes to Skills
- Procedure / cached TI sections informational only in plans

## Required Capabilities

Inferred from the objective and repository context.

- procedure-playbook-ingest
- procedure-knowledge-query
- plan-procedure-context-section
- ti-offline-cache-store
- ti-cache-refresh-cli
- cached-github-stars-provider
- ti-cache-golden-record-testing
- knowledge-steward-procedure-workflow

**Domains detected:** knowledge, github, plan

Human intent also requires: gh auth boundary for cache refresh, fail-closed without
credentials, extend existing Knowledge Steward + TI live Skills.

## Reusable Capabilities Found

Approved Compass Skills ranked for this objective (deterministic matcher).

| Skill | Score | Notes |
|---|---:|---|
| `knowledge-steward` | 0.5571 | procedure ingest + query |
| `technology-intelligence-live` | 0.4929 | cache refresh + cached provider |
| `candidate-promotion` | 0.4286 | procedure promotion ceiling unchanged |
| `github-integration` | 0.3643 | gh CLI for cache refresh |
| `capability-planning` | 0.3643 | plan writer integration |
| `implementation-planning` | 0.3643 | this plan |
| `testing-validation` | 0.3 | validation evidence |
| `security-review` | 0.3 | TI/procedure boundary review |

Prefer in implementation manifests: `knowledge-steward`, `technology-intelligence-live`,
`github-integration`, `capability-planning`.

### Capability Gaps

No new Skill required by default; extend existing Skills unless Captain requests
`procedure-playbooks` dedicated Skill.

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
| `know-adr-023` | decision | — | ADR-023: Performance knowledge ingest and live GitHub Stars TI (v1.11.0 M7) |
| `know-adr-021` | decision | — | ADR-021: Knowledge Steward with stdlib keyword index (v1.9.0 M5) |

## Task Graph

**Human-authored M8 phases:**

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| T-A | Procedure playbook ingest mapper + `--from-store procedures` | — | yes (vs T-C) |
| T-B | Plan writer **Procedure Context** section | T-A | no |
| T-C | TI cache store + `refresh-ti-cache.sh` + cached provider | — | yes (vs T-A) |
| T-D | Extend Skills, doctor, ingest docs | T-A, T-C | no |
| T-E | Tests/evals; ADR-024; docs | T-B–T-D | no |
| T-F | Release prep v1.12.0 | T-E | no |

Generic planner artifact: `.agent/plans/m8-procedure-ti-cache/task-graph.json`

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| Discovery / architecture | `repository-scout` / `architecture-agent` | `capability-planning`, `implementation-planning` |
| Procedure ingest | `implementation-agent` | `knowledge-steward`, `implementation-planning` |
| TI cache adapter | `implementation-agent` | `technology-intelligence-live`, `github-integration`, `security-review` |
| Plan integration | `implementation-agent` | `capability-planning`, `knowledge-steward` |
| Validation | `test-engineer` | `testing-validation`, `security-review` |
| Documentation | `documentation-agent` | `pull-request-preparation`, `knowledge-steward` |

Machine manifests: `.agent/plans/m8-procedure-ti-cache/manifests.json`

## Workstreams

1. **Procedure ingest** — staging playbooks → `kind: procedure`
2. **Procedure Context** — plan section (informational)
3. **TI cache** — refresh CLI, cached provider, golden tests
4. **CLIs + Skills** — extend knowledge-steward, technology-intelligence-live
5. **Harness** — ADR-024, doctor, tests, release

## Parallelization Plan

T-A and T-C can start in parallel. T-B depends on T-A. T-D integrates T-A+T-C.
T-E integrates all. Avoid parallel edits on `orchestrator/plan_writer/`.

## Files Expected to Change

### New

```text
orchestrator/providers/technology_intelligence/ti_cache.py
scripts/refresh-ti-cache.sh
tests/fixtures/ti/cache-recorded/starred-repos-cache.json
tests/fixtures/knowledge/procedures/sample-playbook/
tests/orchestrator/test_m8_procedure_ti_cache.py
.agent/intelligence/.gitkeep (or ti-cache/.gitkeep)
```

### Modified

```text
orchestrator/knowledge/ingest.py
orchestrator/plan_writer/build.py
orchestrator/plan_writer/render.py
orchestrator/providers/technology_intelligence/github_stars_provider.py
orchestrator/providers/technology_intelligence/file_provider.py
scripts/ingest-knowledge.sh
scripts/query-technology-intelligence.sh
.cursor/skills/knowledge-steward/SKILL.md
.cursor/skills/technology-intelligence-live/SKILL.md
docs/integrations/technology-intelligence.md
DECISIONS.md (ADR-024)
TESTING.md, CHANGELOG.md (Unreleased), PROGRESS.md, PROJECT_CONTEXT.md
tests/orchestrator/test_plan_writer.py
```

## Migration and Rollback

1. Rollback tag: `rollback/pre-m8-procedure-ti-cache` @ baseline `c0f02b1`
2. Revert feature branch; cache file is runtime-only under `.agent/intelligence/`
3. Procedure knowledge items removable via re-ingest skip or manual delete under `.agent/knowledge/items/`
4. `COMPASS_TI_PROVIDER=stub` restores pre-M8 TI behavior

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Stale TI cache misleads planning | Wrong discovery signals | Explicit refresh CLI; cache timestamp in JSON; document staleness |
| Procedure staging ingested before Captain review | Premature playbook surfacing | Ingest explicit CLI only; default plans empty until Captain ingests |
| Cache file contains private repo names | Local leak if committed | gitignore `.agent/intelligence/ti-cache/`; redact in docs |
| CI network leakage | Nondeterministic tests | Stub default; golden cache fixtures only |
| Scope creep to Notion ingest | Delay M8 | ADR-024 explicitly defers Notion/NotebookLM |

## Evaluation Strategy

After implementation (post-approval), success by:

- Acceptance criteria checked
- Doctor / tests / evals green
- Stub CI identical to v1.11.0 for default env
- Fixture procedure ingest → Procedure Context populated
- Cached provider with golden fixture returns validated candidates
- `refresh-ti-cache.sh` fails closed without gh auth

## Learning Plan

Retain under `.agent/plans/m8-procedure-ti-cache/`:

- `resolve.json`, `task-graph.json`, `manifests.json`
- Link issue, branch, PR, evidence after execution

Feeds M9+ optional approved-procedure root, TTL cache hints, broader TI providers.

## Autonomy Budget

After approval, create `.agent/budgets/m8-procedure-ti-cache.md`.

- Maximum iterations: 20
- Maximum failed validation cycles: 5
- Maximum estimated cost: Captain-defined
- Maximum elapsed time: 5 working days
- Maximum TI cache refresh batches per plan: 5 (M8-specific)
- Budget ledger path: `.agent/budgets/m8-procedure-ti-cache.md`

## Definition of Done

- All Acceptance Criteria checked
- Doctor / tests / evals green
- Security review recorded
- ADR-024 accepted
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
- **Approved revision:** Procedure Context always render; separate github-stars-cached; staging+approved ingest; v1.12.0; procedure-playbooks Skill
- **Issue:** #66
- **Branch:** feature/66-m8-procedure-ti-cache
- **Rollback:** rollback/pre-m8-procedure-ti-cache @ c0f02b1
- **Feature PR:** #67 (merged)
- **Release:** v1.12.0 (2026-08-24)
