# Implementation Plan — N1 Operational Reconciliation & Development Closeout

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `n1-operational-reconciliation` |
| Issue | *(Captain files before/on approval — agent cannot create GitHub issues)* |
| Notion | [Persistent Project Overseer](https://app.notion.com/p/3eae6a901c438109ba3af1de2982826a) · consolidation track (N1–N3) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.71.0** @ `15e8866` (#235 merged; Level 2 COMPLETE) |
| Proposed branch | `cursor/<issue>-n1-operational-reconciliation-673a` |
| Proposed rollback | `rollback/pre-n1-operational-reconciliation` @ `15e8866` |
| Proposed release | **v1.71.1** |
| Captain | Logan Ware |
| Created | 2026-10-22 |

## Approval record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR |

## Request

Treat **v1.71.0** as a consolidation checkpoint. Reconcile open GitHub issues,
active/historical plans, operator docs, release records, and evidence so every
tracked item is classified with a source-backed disposition. Extend the
read-only Project Overseer with an optional **closeout-readiness** assessment.
Define follow-on **N2** (product integration validation) and **N3** (adaptive
intelligence validation) plans. Keep Specialized Model **Level 3**
(`specialized-model-level-3`) on file as **DEFERRED** until N1–N3 evidence
justifies large-GPU spend.

## Problem Statement

NorthStar’s orchestration, Cognitive Core (C1–C7), oversight, Behavior Loop,
and Specialized Model Levels 0–2 are implemented, but project memory and
GitHub trackers lag reality: completed work remains open (#220, #222 and
likely older review/install issues), `docs/INDEX.md` omits newer `northstar`
surfaces, README/PROJECT_CONTEXT skill counts disagree with the filesystem
(47 vs 48), and roadmap **C2** (product install) collides with Cognitive Core
**C2** (memory retrieval). Approving Level 3 GPU expansion before closing this
gap risks spend without a reliable release baseline or end-to-end product proof.

## Desired Outcome

1. **Closeout ledger** under `.agent/evidence/n1-operational-reconciliation/`
   classifying each open issue and stale plan as
   `completed | superseded | deferred | still_actionable`, with PR/commit/test
   evidence links and recommended disposition (Captain closes issues — agent
   does not auto-close).
2. **Documentation drift fixed:** `docs/INDEX.md` covers current launcher
   surfaces; README / PROJECT_CONTEXT skill counts match `.cursor/skills/`;
   track namespaces documented (e.g. `roadmap/C2` vs `cognitive/C2`).
3. **Release ↔ milestone traceability** in PROGRESS / CHANGELOG / plan mirrors.
4. **Overseer closeout-readiness** (read-only): optional
   `northstar status closeout` (or oversight subcommand) producing a
   reviewable report; authority flags remain false; no auto-apply.
5. **Follow-on plan stubs** for N2 and N3 at AWAITING APPROVAL (or deferred
   drafts under `docs/plans/`), preserving Captain gates.
6. **Level 3** mirror marked **DEFERRED** (prerequisites: N1–N3 + Level 0–2
   proof-of-value); harness proposal preserved, not deleted.
7. Doctor, schema validation, and relevant regression checks pass; release
   **v1.71.1**.

## Acceptance Criteria

- [ ] Ledger covers all currently open issues (#222, #220, #170, #169, #164,
      #147, #146, #144) plus active plan documents; each row has status,
      evidence refs, and recommended disposition
- [ ] No silent GitHub issue closes or merges; dispositions are proposals for
      Captain action
- [ ] `docs/INDEX.md` lists Cognitive Core, oversight, specialized, and
      Behavior Loop operator surfaces (not only skills/review)
- [ ] README + PROJECT_CONTEXT skill counts match filesystem; specialists = 12
- [ ] Track-namespace note removes C2 ambiguity (roadmap vs Cognitive Core)
- [ ] Closeout-readiness report is fail-closed behind existing status/oversight
      gates; `applied` / authority mutation flags locked false
- [ ] N2 + N3 follow-on plans written (stubs OK); Level 3 marked DEFERRED with
      prerequisites recorded
- [ ] Doctor + relevant unit/regression tests pass; evidence recorded
- [ ] CHANGELOG **v1.71.1**; PROGRESS points to N2 (or Captain-chosen next)

## Non-Goals

- Approving or implementing Specialized Model Level 3 / paid large-GPU jobs
- Training or deploying specialized model weights
- Auto-closing GitHub issues or auto-merging PRs
- Promoting Skills/policies or expanding live model-routing authority
- Full product-repo lifecycle proof (that is **N2**)
- Measuring adaptive-intelligence improvement over time (that is **N3**)
- Live trading / AHF execution

## Assumptions

1. GitHub state + merged PRs + tests/evidence are authoritative over stale prose.
2. Captain files the tracking issue and performs issue close/reopen actions.
3. `captain-compass-sandbox` refresh and/or `bitcoin-data-collector` (#164)
   remain N2 target choices — N1 only records the recommendation.
4. Capability-plan ML task suggestion for this objective is **overridden**; N1
   is governance/docs + bounded Overseer reporting, not training code.

## Open Questions (defaults if approve as written)

1. **Release version:** **v1.71.1** (closeout patch; Level 3 stays proposed
   **v1.72.0** when later approved) → default **yes**.
2. **Closeout CLI:** add `northstar status closeout [--repo]` composing
   existing snapshot/explain findings + ledger checklist → default **yes**
   (reuse `COMPASS_STATUS_ENABLED`; no new authority).
3. **Issue closes:** agent posts disposition comments only when
   `gh`/permissions allow; Captain closes → default **yes**.
4. **N2 target:** recommend finishing #164 (`bitcoin-data-collector`) **or**
   refreshing `captain-compass-sandbox` to current control version; Captain
   picks at N2 approval → default **document both; prefer #164 continuity**.
5. **Skill count:** treat `inodes` + `context-inodes` as two Skills (48) and
   update docs → default **yes** (verify registry/doctor expectations).

## Current-State Analysis

| Asset | Role |
|---|---|
| Open issues #220/#222 | Likely completed by #221/#224 — need acceptance verify |
| Open #144–#170, #164 | Older review/security/install trackers — reconcile vs code |
| `docs/INDEX.md` | Stale vs `scripts/northstar` help |
| `IMPLEMENTATION_PLAN.md` was Level 3 | Now superseded as active-next by this plan |
| `docs/plans/SPECIALIZED_MODEL_LEVEL_3.md` | Preserve as DEFERRED |
| Overseer `status` / `oversight` | Read-only compose; extend with closeout report |
| Skills on disk | 48 directories; docs say 47 |
| Agents | 12 profiles — matches docs |

## Proposed Architecture

```text
N1 closeout
  ├── inventory (issues, plans, PRs, VERSION)
  ├── ledger (status + evidence + disposition)
  ├── docs drift (INDEX, README, track namespaces)
  ├── status closeout (read-only report; optional)
  └── follow-ons (N2, N3 stubs; Level 3 DEFERRED)
```

## Workstreams

| ID | Scope | Profile / Skills |
|---|---|---|
| W1 | Issue/plan ledger + evidence package | `repository-scout`, `harness-gc`, `github-integration` |
| W2 | Docs INDEX / counts / track namespaces / PROGRESS | `documentation-agent`, `pull-request-preparation` |
| W3 | Optional `status closeout` report (schema + tests) | `project-overseer`, `implementation-agent` |
| W4 | N2/N3 plan stubs + Level 3 DEFERRED mirror | `implementation-planning`, `capability-planning` |
| W5 | Doctor / unit / regression + CHANGELOG v1.71.1 | `testing-validation` |

## Files Expected to Change

- `IMPLEMENTATION_PLAN.md` (this plan; post-merge COMPLETE)
- `docs/plans/N1_OPERATIONAL_RECONCILIATION.md`
- `docs/plans/N2_PRODUCT_INTEGRATION_VALIDATION.md` (stub)
- `docs/plans/N3_ADAPTIVE_INTELLIGENCE_VALIDATION.md` (stub)
- `docs/plans/SPECIALIZED_MODEL_LEVEL_3.md` (DEFERRED banner)
- `docs/plans/SPECIALIZED_MODEL_LEVEL_2.md` (next pointer)
- `docs/INDEX.md`, `README.md`, `PROJECT_CONTEXT.md`, `PROGRESS.md`
- `CHANGELOG.md`, `TESTING.md` (closeout command if added)
- `DECISIONS.md` (ADR for consolidation track / Level 3 deferral)
- `orchestrator/status/` (+ schema/tests) if W3 approved as written
- `scripts/run-status.sh`, `scripts/northstar`, `scripts/doctor.sh` as needed
- `.agent/evidence/n1-operational-reconciliation/`
- `.agent/budgets/n1-operational-reconciliation.md`
- `.agent/plans/n1-operational-reconciliation/` (capability artifacts)

## Testing Strategy

- Unit: closeout report schema; fail-closed without status gate; authority flags
- Doctor: schemas + INDEX/skill-count consistency checks if already supported
- Regression: existing status/oversight/specialized hermetic tests still pass
- Manual: ledger reviewed against `gh issue list` + merged PR list

## Security Review

- No new network authority; no auto-close via privileged tokens beyond read
- Closeout report must not embed secrets from evidence paths
- Level 3 deferral does not weaken cost-ack or weight-out-of-repo rules

## Rollback Plan

Tag `rollback/pre-n1-operational-reconciliation` @ `15e8866`; revert PR.
Deferred Level 3 plan remains recoverable from git history / mirror file.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Closing issues that still have residual gaps | Ledger proposes only; Captain verifies acceptance criteria |
| Scope creep into N2/N3 implementation | Hard non-goals; stubs only |
| Skill-count / doctor false positives | Verify registry compile before asserting 48 |
| Capability-plan suggested python-ml | Explicit override in this plan |

## Capability planning (merged; corrected)

Machine artifacts: `.agent/plans/n1-operational-reconciliation/`.
Auto-ranked `python-ml` is **not** used. Preferred Skills:
`harness-gc`, `project-overseer`, `github-integration`,
`implementation-planning`, `repository-discovery`, `testing-validation`,
`pull-request-preparation`.

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 12 |
| Wall time | 8 hours |
| After approval | implement → validate → commit → open PR |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve n1-operational-reconciliation** (or revise open questions). After
approval, First Mate will branch, implement, validate, **commit, and open the
PR**. Merge remains yours. Please file a GitHub issue for tracking (agent
cannot).

**Note:** Approving N1 does **not** approve Specialized Model Level 3 or paid
GPU execution. Level 3 remains DEFERRED until N1–N3 evidence and a separate
explicit approval.
