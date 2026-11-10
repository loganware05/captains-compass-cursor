# Implementation Plan — XRV W1: Release Integrity & Project-State Reconciliation

- Status: **COMPLETE** (PR open)

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** (PR [#262](https://github.com/loganware05/captains-compass-cursor/pull/262)) |
| Plan ID | `xrv-release-integrity` |
| Issue | [#261](https://github.com/loganware05/captains-compass-cursor/issues/261) |
| Baseline | **v1.83.0** @ `987a49c` (merged I6 / #260) |
| Branch | `feature/261-xrv-release-integrity` |
| Rollback | `rollback/pre-xrv-release-integrity` @ `987a49c` |
| Proposed release | **v1.83.1** |
| Program | Cross-Repository Engineering Intelligence Validation (Nov 2026) |
| Sources | Notion roadmap (2026-11-10); ChatGPT outline; Cross-Repository Roadmap PDF; Repository Assessment 2026-11-09 |
| Approved by | Logan Ware (Captain) — “Proceed with the first prompt” + multi-agent handoff amendment |
| Approval date | 2026-11-10 |

## Problem Statement

NorthStar’s next cycle should prove existing orchestration improves real engineering
outcomes across independent repos—not add more agent features first.

Verified drift already matches the Notion Immediate Sprint:

1. **NorthStar:** `VERSION` = `1.83.0`, but `README.md` still says **1.76.0**;
   `PROGRESS.md` still says PR [#260](https://github.com/loganware05/captains-compass-cursor/pull/260)
   is open though it **merged** 2026-11-09 @ `987a49c`; issue
   [#259](https://github.com/loganware05/captains-compass-cursor/issues/259)
   (and I1–I5 issues #249/#251/#253/#255/#257) remain **OPEN**.
2. **TrapHouse Kitchen:** Slice 17 PR
   [#35](https://github.com/loganware05/TrapHouseKitchen/pull/35) merged, while
   project status docs reportedly still say “implementing” (needs repo-local verify).
3. There is no shared, schema-validated **Experience Evidence Record** that lets an
   auditor reconstruct issue → plan → implement → test → review → merge → verified
   outcome across pilot repos.
4. CI does not fail on README/`VERSION` release-document drift.

N1 closeout (`status closeout`) already exists but does not close this specific
release-integrity gap for the Cross-Repo Validation (XRV) program.

## Desired Outcome

Ship a **v1.83.1** control-repo patch that:

1. Reconciles NorthStar release/memory docs with GitHub truth for I6 (and proposes
   Captain-gated closures for completed I1–I5 issues—no silent auto-close).
2. Adds machine-checked release/document consistency checks (doctor and/or unit
   tests in CI).
3. Introduces a schema + fixture + gated emit/validate path for a cross-repository
   **Experience Evidence Record** (EER), reusing fields from existing
   `experience` / `execution-run` / closeout concepts without granting authority.
4. Records the XRV program as a durable docs plan under `docs/plans/`, with
   Week 1–2 exit criteria and explicit deferrals (Level 3, live money, auto-merge).

## In Scope (this plan)

| Workstream | Deliverable |
|---|---|
| WS0 Discovery | Confirm merge SHAs, open issues, current doctor/version checks; cite Notion + outline |
| WS1 NorthStar closeout | Align `README.md` version, `PROGRESS.md`, `IMPLEMENTATION_PLAN.md`, `CHANGELOG`/`PROJECT_CONTEXT` as needed; closeout evidence packet; Captain-gated issue disposition list for #259 and I1–I5 |
| WS2 Drift CI | Hermetic check: `VERSION` ↔ README current-version line; optional CHANGELOG heading presence; wire into `tests/run.sh` / doctor |
| WS3 EER schema | `orchestrator/schemas/experience-evidence-record.schema.json`; fixture under `.agent/evidence/xrv/`; gated `northstar`/`scripts` validate or emit (fail-closed; authority locks false) |
| WS4 XRV docs | `docs/plans/XRV_CROSS_REPOSITORY_VALIDATION.md` + INDEX/handbook pointer; ADR for program kickoff |
| WS5 Validation | Doctor + unit tests + evidence under `.agent/evidence/xrv-release-integrity/` |

## Out of Scope (explicit)

- TrapHouse / Bitcoin / PrizePicksBot **product** implementation or payment/trading changes
- Live Sentry / Apify / T3 / Scrimba / WorkOS calls
- Specialized Model Level 3 (#237 stays deferred)
- Auto-closing GitHub issues without Captain confirmation
- Eight-pillar readiness assessor (`northstar assess readiness`) — foundation backlog item; separate plan
- Adaptive skill-transfer benchmark (Weeks 8–10)
- Standalone NorthStar application / fully autonomous merge

## Multi-agent orchestration (Captain amendment)

Captain directed First Mate to hand off pilot-repo work to other agents while
NorthStar W1 proceeds here.

| Agent / thread | Project | Mode | Objective |
|---|---|---|---|
| First Mate (this thread) | `captains-compass-cursor` | Implement W1 | Release integrity, drift CI, EER schema, XRV docs |
| TrapHouse handoff thread | `TrapHouseKitchen` @ `/Users/loganware/TrapHouseKitchen` | Read-only discovery → draft plan | Reconcile STATUS/PROGRESS vs merged PR #35; inventory payment-safety tests/evidence; **no product edits until that repo’s plan is approved** |
| Bitcoin handoff thread | `bitcoin-data-collector` @ `/Users/loganware/bitcoin-data-collector` | Read-only discovery → draft plan | Paper-validation continuity state, PR #16 status, live-execution deny checks; **no live trading / no product edits until approved** |

Notes:

- `delegate_task` child-agent mode is unavailable on this host (provider constraints);
  handoffs use top-level `t3_thread_launch` bound to each T3 project.
- Native Cursor subagents remain available inside a single checkout when needed.
- PrizePicksBot stays later (transfer-learning pilot); local clone under
  `Documents/Personal/Code/PrizePicksBot` exists.

## Companion work (parallel discovery; not claimed complete in NorthStar PR)

| Repo | Need | Access now |
|---|---|---|
| TrapHouseKitchen | Reconcile STATUS/PROGRESS vs merged PR #35; verify tests/deploy evidence | T3 project + `/Users/loganware/TrapHouseKitchen` |
| bitcoin-data-collector | Paper-continuity baseline (repo exists; not “unmade”) | T3 project + `/Users/loganware/bitcoin-data-collector` |
| PrizePicksBot | Access inventory / mock-only onboarding later | GitHub OK; local clone exists |

## Current → Desired Behavior

| Area | Current | Desired |
|---|---|---|
| README version | Shows 1.76.0 | Matches `VERSION` (1.83.0 → then 1.83.1 on release) |
| PROGRESS | Claims PR #260 open / I6 opening PR | Merged closeout; next plan = this XRV W1 |
| Issues I1–I6 | Open despite merged PRs | Disposition proposals + Captain-gated close |
| Drift detection | Installer copies VERSION; no README sync test | CI fails on mismatch |
| Cross-repo evidence | Per-milestone ad hoc evidence dirs | Shared EER schema + one reconstructed I6 cycle fixture |

## Acceptance Criteria

- [x] `README.md` current version matches `VERSION`
- [x] `PROGRESS.md` / plan status reflect I6 merged @ `987a49c` and this plan as active after approval
- [x] Automated drift test fails when README version ≠ `VERSION` (hermetic)
- [x] EER JSON Schema validates a fixture that reconstructs the I6 issue→PR→evidence cycle
- [x] EER authority fields locked (`approved_for_execution: false`, no auto-close / no auto-promote)
- [x] `docs/plans/XRV_CROSS_REPOSITORY_VALIDATION.md` exists with Week 1–2 exit criteria and deferrals
- [x] Doctor + `./tests/run.sh` (applicable unit tests) pass; evidence recorded
- [x] ADR recorded; rollback tag documented
- [x] No live provider network; no TrapHouse/Bitcoin product file changes in this PR

## Assumptions

1. Captain wants XRV W1 on the **control repo** before TrapHouse local reconciliation.
2. Closing I1–I5/#259 is allowed only after Captain confirms acceptance (plan may prepare close comments).
3. EER is additive; existing `experience.schema.json` remains; EER may reference those IDs.
4. Patch release **v1.83.1** is preferred over a minor bump for reconciliation + schema.

## Open Questions (defaults applied; Captain may override)

1. **Issue closures:** Default = prepare close comments + leave Captain to confirm/close (no silent auto-close).
2. **TrapHouse path:** Resolved — `/Users/loganware/TrapHouseKitchen` (T3 project present).
3. **EER CLI surface:** Default = gated validate under `northstar status` or thin `evidence` alias; finalize in architecture step.
4. **Notion:** Default = mirror only; repo remains authoritative.

## Risks

| Risk | Mitigation |
|---|---|
| Silent issue closure | Proposal-only; Captain confirms each close |
| Schema sprawl vs experience/execution-run | Explicit mapping table in docs; EER wraps/extends |
| Scope creep into TrapHouse payments | Hard out-of-scope; separate plan |
| Stale local branch vs main | Branch from `main` @ `987a49c` after approval |

## Independent Workstreams

1. **Docs/closeout** — README/PROGRESS/CHANGELOG/PROJECT_CONTEXT/XRV plan doc
2. **Drift CI** — test + doctor hook
3. **EER schema + fixture + gated validate** — orchestrator + tests
4. **Evidence + ADR + budget** — `.agent/evidence/`, `DECISIONS.md`, budget file

(No DB migrations. Capability-plan suggested `task-impl-database` is **rejected** for this objective.)

## Required Capabilities (human-adjusted)

- Release/document reconciliation
- Schema design + hermetic validation
- CI/doctor wiring
- Project memory documentation
- Approval-boundary preservation

## Task Graph (human-adjusted)

| Task ID | Objective | Dependencies |
|---|---|---|
| `task-discovery` | Confirm GitHub/doc drift + existing closeout/experience schemas | — |
| `task-architecture` | EER field map + drift-check contract + rollback | task-discovery |
| `task-impl-docs-ci` | Align docs; add drift test/doctor; XRV plan doc | task-architecture |
| `task-impl-eer` | Schema, fixture, gated validate/emit | task-architecture |
| `task-validation` | Doctor + unit tests + evidence packet | task-impl-docs-ci, task-impl-eer |
| `task-security-review` | Confirm no secrets, no authority elevation | task-impl-eer |
| `task-documentation` | ADR, CHANGELOG 1.83.1, PROGRESS, handbook/INDEX | task-validation, task-security-review |

## Evaluation Strategy

- Hermetic unit tests for schema + drift detector
- Doctor green
- Manual checklist: independent reader can follow I6 EER fixture from issue → merge SHA → scorecard path
- Adversarial pass: ensure no auto-approval / auto-close flags

## Learning Plan

- Retain plan artifacts under `.agent/plans/xrv-release-integrity/` (capability resolve already drafted under `release-integrity-reconciliation/` — rename/align on implementation)
- EER fixture becomes the first cross-repo-program exemplar for later TrapHouse/Bitcoin records

## Approval Boundary

**APPROVED** 2026-11-10 by Captain (“Proceed with the first prompt” + multi-agent handoff).

First Mate will:

1. Create GitHub issue + feature branch from `main` + rollback tag
2. Launch TrapHouse + Bitcoin discovery handoff threads (plan-only in those repos)
3. Implement NorthStar in-scope workstreams only
4. Validate, evidence, PR

Pilot-repo product edits require **their own** approved plans; discovery threads must stop at AWAITING APPROVAL there.

## Autonomy Budget

See `.agent/budgets/xrv-release-integrity.md` (created with this plan).

| Limit | Value |
|---|---|
| Iterations | 10 |
| Wall time | 6 hours |
| Scope | Control-repo W1 only; no live providers; no pilot product code in this PR |

## Rollback

1. Revert the release PR / reset to rollback tag
2. Remove EER schema/CLI if needed; drift test is additive
3. Docs-only portions can be reverted independently
