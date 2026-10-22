# Implementation Plan — N1 Operational Reconciliation & Development Closeout

- Status: **COMPLETE** (pending merge)

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** (pending merge) |
| Plan ID | `n1-operational-reconciliation` |
| Issue | *(placeholder — Captain files GitHub issue; agent cannot create issues)* |
| Notion | [Persistent Project Overseer](https://app.notion.com/p/3eae6a901c438109ba3af1de2982826a) · consolidation track (N1–N3) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.71.0** @ `c7679bf` (#236 plan docs on main) |
| Branch | `cursor/n1-operational-reconciliation-673a` |
| Rollback | `rollback/pre-n1-operational-reconciliation` @ `c7679bf` |
| Release | **v1.71.1** |
| Captain | Logan Ware |
| Created | 2026-10-22 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-10-22 |
| Notes | Explicit reply: `approve n1-operational-reconciliation`. Standing order ⇒ implement → validate → commit → open PR |

## Request

Treat **v1.71.0** as a consolidation checkpoint. Reconcile open GitHub issues,
active/historical plans, operator docs, release records, and evidence so every
tracked item is classified with a source-backed disposition. Extend the
read-only Project Overseer with an optional **closeout-readiness** assessment.
Define follow-on **N2** (product integration validation) and **N3** (adaptive
intelligence validation) plans. Keep Specialized Model **Level 3**
(`specialized-model-level-3`) on file as **DEFERRED** until N1–N3 evidence
justifies large-GPU spend.

## Acceptance Criteria

- [x] Ledger covers open issues #222, #220, #170, #169, #164, #147, #146, #144
      plus active plans; each row has status, evidence refs, disposition
- [x] No silent GitHub issue closes or merges; dispositions are proposals
- [x] `docs/INDEX.md` lists Cognitive Core, oversight, specialized, Behavior Loop
- [x] README + PROJECT_CONTEXT skill counts match filesystem (47 Skills with
      `SKILL.md`; `inodes/` is content store); specialists = 12
- [x] Track-namespace note removes C2 ambiguity
- [x] `status closeout` fail-closed; authority / `issues_auto_closed` locked false
- [x] N2 + N3 follow-on stubs; Level 3 DEFERRED
- [x] Doctor + unit/regression tests pass; evidence recorded
- [x] CHANGELOG **v1.71.1**; ADR-091

## Non-Goals

- Approving or implementing Specialized Model Level 3 / paid large-GPU jobs
- Training or deploying specialized model weights
- Auto-closing GitHub issues or auto-merging PRs
- Promoting Skills/policies or expanding live model-routing authority
- Full product-repo lifecycle proof (**N2**)
- Measuring adaptive-intelligence improvement over time (**N3**)

## Rollback Plan

Tag `rollback/pre-n1-operational-reconciliation` @ `c7679bf`; revert PR.

## Approval Boundary

Implementation authorized by Captain approval recorded above.
Level 3 GPU work remains **not** approved.
