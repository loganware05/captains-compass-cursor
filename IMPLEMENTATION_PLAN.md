# Implementation Plan — C1 Cognitive Core Source of Truth

- Status: **APPROVED** (implementation complete on feature branch; awaiting PR)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** (impl complete; PR pending) |
| Plan ID | `c1-cognitive-core-source-of-truth` |
| Linear | [OVA-72](https://linear.app/ovaltechnologysolutions/issue/OVA-72/c1-cognitive-core-source-of-truth-git-sync-versioned-project-state) · Project [P-OVA-6](https://linear.app/ovaltechnologysolutions/project/northstar-cognitive-core-445cdc0f12d6) · Milestone **C1 — Source of Truth** |
| Notion | [Cognitive Core Design](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (C1 gate only) |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.59.0** @ `9b9d6bd` |
| Branch | `feature/OVA-72-c1-cognitive-core-source-of-truth` |
| Rollback | `rollback/pre-c1-cognitive-core-source-of-truth` @ `9b9d6bd` |
| Proposed release | **v1.60.0** |
| Captain | Logan Ware |
| Created | 2026-10-13 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| When | 2026-10-13 — explicit “approve C1” |
| Notes | Defaults as written: `brain` CLI, local-git-only, `.agent/project-state/` |

## Request

Ship Cognitive Core **C1 only**: read-only Git sync and versioned, SHA-cited project-state snapshots so a merged change is reflected at the correct SHA or sync explicitly declares **stale**. Reuse M51 Project Overseer status facts; do not expand into C2–C5.

## Problem Statement

Overseer `status` snapshots explain drift but do not provide a durable, versioned **project-state** index that Cognitive Core (and later Adaptive Intelligence) can treat as the source of truth independent of any chat model. Without C1, later retrieval/routing/training work would re-derive facts ad hoc.

## Desired Outcome

1. Gated operator surface `northstar brain sync|status|show` (name pending Captain confirm).
2. Schema-validated project-state snapshots under `.agent/project-state/`.
3. Freshness contract: HEAD (and optional GitHub merge tip) matches snapshot SHA, else `freshness: stale`.
4. Hermetic CI; optional live `gh` for GitHub enrichment never required.
5. Always `approved_for_execution: false` / `authority_mutation: false`.

## Acceptance Criteria

- [x] `COMPASS_BRAIN_ENABLED=1` required; unset → fail closed
- [x] `brain sync` writes a versioned snapshot with `repository_sha`, `snapshot_id`, citations, freshness
- [x] After local HEAD moves past last sync, `brain status` reports **stale** (or sync refreshes and becomes fresh)
- [x] Snapshot schema + unit tests; doctor aware of new gate/schemas
- [x] Composes/reuses M51 status git/memory facts; does not auto-rewrite `PROJECT_CONTEXT.md` / ADRs / `PROGRESS.md`
- [x] No live network required for CI; GitHub deferred (local-git-only)
- [x] Evidence under `.agent/evidence/c1-cognitive-core-source-of-truth/VALIDATION.md`
- [x] `PROGRESS.md` / `CHANGELOG.md` / ADR updated on ship
- [ ] PR opened against `main` with Linear link

## Non-Goals

- C2 memory/retrieval / gold-set accuracy
- C3 Adaptive Intelligence routing / model registry
- C4 REA investigate adapter
- C5 Specialized Model training bridge / LoRA
- HTTP `/v1/*` server (contracts may be documented as *future*; CLI is C1 deliverable)
- Separate external `cognitive-core` package extract (defer; keep module in `orchestrator/` for C1)
- Live Kimi / OpenRouter required for CI
- Captain-approval handoff or plan auto-approve
- Silent canonical memory rewrites

## Assumptions

1. Captain wants C1 scoped tightly so Specialized Model S1 remains a parallel research checklist, not this plan.
2. Local Git is authoritative for SHA; GitHub enrichment is optional and read-only.
3. Capability-plan ranked `python-ml` for this objective — **override**: C1 is orchestrator/Python service work, not ML training. Prefer Skills: `project-overseer`, `github-integration`, `node-engineering`/`python` patterns already in orchestrator, `testing-validation`, `implementation-planning`.

## Open Questions (for Captain at approval)

1. **CLI name:** confirm `northstar brain …` vs extending `northstar status …` (proposal: **`brain`** — keeps Overseer advisory and Core index distinct).
2. **GitHub in C1:** include opt-in `COMPASS_BRAIN_GITHUB=1` PR/CI tip check, or ship **local-git-only** and defer GitHub to a fast follow?
3. **Store path:** confirm `.agent/project-state/` (proposal) vs Notion’s older `.agent/state/` naming.

Default if Captain says “approve as written”: `brain` CLI, **local-git-only** for C1 (GitHub deferred), `.agent/project-state/`.

## Current-State Analysis

| Asset | Role for C1 |
|---|---|
| M51/M52 `orchestrator/status/` | Reuse SHA, drift, memory probes; do not replace |
| `.agent/status/` | Overseer artifacts only |
| Behavior loop M46–M54 | Out of scope; may later consume project-state |
| Knowledge steward | Out of scope (C2) |
| Live StatusProvider HTTP | Out of scope |

## Proposed Architecture

```text
Developer / First Mate
        │
        ▼
northstar brain (COMPASS_BRAIN_ENABLED)
        │
        ├── sync  → collect local git facts (+ optional gh later)
        │            compose optional status snapshot id
        │            write .agent/project-state/snapshots/<id>.json
        │            update latest pointer + freshness
        ├── status → report latest snapshot + freshness vs HEAD
        └── show   → print one snapshot (schema-validated)
```

- New package: `orchestrator/cognitive/` (or `orchestrator/brain/`) — sync, store, freshness, CLI wiring via `scripts/run-brain.sh` + `scripts/northstar`.
- Schema: `orchestrator/schemas/project-state-snapshot.schema.json`.
- Invariants: read-only git; no writes outside `.agent/project-state/` and evidence; authority flags const false.

## Required Capabilities

(From capability-plan + human override)

- Repo/Git fact collection and schema-validated persistence
- Fail-closed enable gates
- Hermetic unit/integration tests + doctor
- Documentation / ADR / progress

## Reusable Capabilities Found

- `project-overseer` / `orchestrator.status` (SHA, drift patterns)
- `github-integration` (patterns; live gh optional/deferred)
- `testing-validation`, `autonomy-budget`, `pull-request-preparation`

## Technology Intelligence Candidates

> External candidates are **NOT APPROVED FOR EXECUTION**.

- REA / Kimi / Specialized Model docs are **out of scope** for C1 (metadata only).

## Task Graph

| Task ID | Objective | Dependencies |
|---|---|---|
| `task-discovery` | Confirm status reuse points and gate patterns | — |
| `task-architecture` | Schema + store + freshness contract + CLI map | discovery |
| `task-impl-brain` | Implement sync/status/show + northstar wiring | architecture |
| `task-validation` | Unittests, doctor, evidence pack | impl |
| `task-documentation` | ADR, PROGRESS, CHANGELOG, plan COMPLETE banner | validation |

Machine artifact: `.agent/plans/c1-cognitive-core-source-of-truth/` (capability-plan; ML task in that artifact is **superseded** by `task-impl-brain`).

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| discovery | `repository-scout` | `repository-discovery`, `project-overseer` |
| architecture | `architecture-agent` | `capability-planning`, `code-structure-cleanup` |
| impl | `implementation-agent` | `autonomy-budget`, `github-integration` (if GitHub), `project-overseer` |
| validation | `test-engineer` | `testing-validation` |
| docs | `documentation-agent` | `pull-request-preparation` |

## Workstreams

| ID | Scope | Parallel? |
|---|---|---|
| W1 | Schema + store + freshness | no |
| W2 | CLI + northstar help + enable gate | after W1 |
| W3 | Tests + doctor + evidence | after W2 |
| W4 | Docs / ADR / release notes | after W3 |

## Files Expected to Change

- `orchestrator/cognitive/` (new) or `orchestrator/brain/` (new)
- `orchestrator/schemas/project-state-snapshot.schema.json` (new)
- `scripts/northstar`, `scripts/run-brain.sh` (new)
- `tests/orchestrator/test_c1_cognitive_core_source_of_truth.py` (new)
- `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md` (ADR)
- `docs/plans/C1_COGNITIVE_CORE_SOURCE_OF_TRUTH.md`
- `.agent/budgets/c1-cognitive-core-source-of-truth.md`
- `.agent/evidence/c1-cognitive-core-source-of-truth/`

## Testing Strategy

- Unit: sync produces valid snapshot; stale detection when HEAD advances; gate fail-closed
- Regression: M51 status tests still pass
- Doctor: new schema/gate registered without requiring live GitHub
- Evidence matrix: hermetic CLI capture under `.agent/evidence/c1-cognitive-core-source-of-truth/`

## Security Review

- Read-only git / optional read-only `gh`
- No secrets in snapshots; redact if any env bleeds
- Fail closed without enable flag
- Never mutate authority or canonical memory

## Accessibility Review

Not applicable (CLI/orchestrator only).

## Migration Plan

New gated feature; default off. Existing installs unaffected until `COMPASS_BRAIN_ENABLED=1`.

## Deployment Plan

Merge PR → tag/release **v1.60.0** → optional sandbox `update.sh` verification.

## Rollback Plan

- Tag `rollback/pre-c1-cognitive-core-source-of-truth` before implementation
- Revert PR / unset `COMPASS_BRAIN_ENABLED`; delete `.agent/project-state/` if needed (non-canonical)

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Duplicate Overseer | Distinct `brain` surface; compose status ids, don’t fork drift logic blindly |
| Scope creep into C2/C3 | Hard non-goals; Linear milestone C1 only |
| Live GitHub flaky CI | Hermetic fixtures; GitHub deferred by default |
| Capability-plan ML misfire | Human override in this plan |

## Evaluation Strategy

- Acceptance criteria checklist
- Unittest + doctor green
- Adversarial review before merge
- Linear OVA-72 → Done only after merge evidence

## Learning Plan

Retain plan artifacts under `.agent/plans/c1-cognitive-core-source-of-truth/` and validation evidence for C2 planning.

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 8 |
| Wall time | 4 hours |
| Cost | Stay within Captain session norms; no paid GPU |
| Stop | Budget Stop Report under `.agent/evidence/` |

Track in `.agent/budgets/c1-cognitive-core-source-of-truth.md`.

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Say **approve C1** (or revise open questions) to proceed: issue already exists (OVA-72); next steps after approval are rollback tag, feature branch/worktree, then implementation.
