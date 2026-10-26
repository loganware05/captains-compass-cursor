# Implementation Plan — N5 Skill-Fit / Routing Feedback

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `n5-skill-routing-feedback` |
| Issue | *(placeholder — create after approval)* |
| Baseline | **v1.75.0** @ `2cd6aef` (#243 merged) |
| Branch | `cursor/n5-skill-routing-feedback-010c` |
| Rollback | `rollback/pre-n5-skill-routing-feedback` *(tag after approval)* |
| Proposed release | **v1.76.0** |
| Track | `consolidation/N5` |
| Captain | Logan Ware |
| Created | 2026-10-26 |
| Sources | Repository State 2026-10-24 (priority 3); N4 hermetic report `LATEST_hermetic.json` |

## Approval record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Notes | Captain said “proceed with N5” after #243 merge — awaiting explicit approval of **this** plan before implementation. |

---

## Request

Use **N4 benchmark deltas** to validate proposed **Skill-fit / routing improvements**, emitting Captain-reviewable proposals with **no automatic policy or weight promotion**.

## Problem Statement

N4 hermetic runs show evidence-informed arms improving primary efficiency and Skill reuse (fixture-driven). Operators need a governed path from those deltas → **routing / Skill-confidence proposals** without silently mutating matcher weights, Experiences apply flags, or policies. Existing `propose-experience-routing` / bounded-autonomy paths must stay proposal-only unless Captain separately applies.

## Desired Outcome

1. Gated CLI: `northstar feedback n5` / `run-n5-feedback.sh`
   (`COMPASS_N5_FEEDBACK_ENABLED` or `--enable-gates`)
2. Ingest N4 report JSON (default `.agent/evidence/n4-cross-stack-benchmark/LATEST_hermetic.json`)
3. Emit schema-validated **N5 feedback packet**:
   - Skill-fit suggestions (which Skills to boost/dampen by stack/difficulty)
   - Routing proposal stubs compatible with existing RoutingProposal shape (`auto_apply: false`, `captain_approved: false`)
   - Validation summary vs N4 deltas (accept_rate, skill_reuse, retrieval, primary efficiency)
4. Optional write under `.agent/routing/proposals/` **without** calling `apply-routing-proposal.sh`
5. Hermetic unit tests + doctor fail-closed
6. Evidence under `.agent/evidence/n5-skill-routing-feedback/`
7. Docs/ADR/CHANGELOG **v1.76.0**; Level 3 remains **DEFERRED**

## Acceptance Criteria

- [ ] Fail-closed without `COMPASS_N5_FEEDBACK_ENABLED` / `--enable-gates`
- [ ] Reads N4 report; refuses missing/invalid N4 input
- [ ] Schema locks: `auto_applied`, `authority_mutation`, `approved_for_execution`, `policy_promoted`, `weights_applied` all **false**
- [ ] Generated RoutingProposal (if any) has `auto_apply=false` and is not applied
- [ ] Feedback packet cites N4 `report_id` + seed + deltas
- [ ] Doctor + unit tests; security review recorded
- [ ] No matcher WEIGHTS file mutation; no Experience auto-adjust; no Level 3
- [ ] N4 plan marked COMPLETE in memory docs (post-merge closeout)
- [ ] CHANGELOG / VERSION / ADR for **v1.76.0**

## Non-Goals

- Calling `apply-routing-proposal.sh` / bounded weight apply
- Policy promotion (M50) or Skill lifecycle auto-advance
- Re-running live multi-repo N4 implements
- Specialized Model Level 3
- Claiming production Skill-fit gains beyond hermetic N4 inputs

## Assumptions

1. N4 hermetic LATEST report on `main` is the default input.
2. Skill-fit suggestions are derived deterministically from N4 deltas + task stack tags (no live LLM required for v1.76.0).
3. Captain may later approve individual routing proposals via existing M4/bounded-autonomy flow — out of band.

## Open Questions (defaults proposed)

| # | Question | Proposed default |
|---|---|---|
| 1 | Auto-write `.agent/routing/proposals/`? | **Yes**, proposal-only files; never apply |
| 2 | Gate | `COMPASS_N5_FEEDBACK_ENABLED` |
| 3 | Release | **v1.76.0** |
| 4 | Minimum delta to suggest boost | `skill_reuse` or `accept_rate` delta ≥ 0.05 |
| 5 | Stacks without positive delta | Emit “no change” note, not a proposal |

## Current-State Analysis

| Item | State |
|---|---|
| N4 | Merged #243 / v1.75.0; hermetic deltas: accept_rate +0.4, skill_reuse +0.057, primary_efficiency +0.117 |
| Experience routing | `propose-experience-routing.sh` — proposal-only |
| Apply path | `apply-routing-proposal.sh` — Captain-flagged only |
| N5 surface | **None** yet |

## Proposed Architecture

```
N4 LATEST_hermetic.json
        │
        ▼
┌──────────────────────┐     optional      ┌─────────────────────────┐
│ orchestrator/        │ ───────────────►  │ .agent/routing/proposals│
│ feedback/n5/         │  proposal-only    │ (auto_apply=false)      │
└─────────┬────────────┘                   └─────────────────────────┘
          │
          ▼
   n5-feedback-report.schema.json → .agent/evidence/n5-skill-routing-feedback/
```

## Workstreams (post-approval)

1. **WS0** — Mark N4 COMPLETE in PROGRESS/plan index; record merge SHA
2. **WS1** — Schema + `orchestrator/feedback/n5` (ingest, suggest, service)
3. **WS2** — CLI `run-n5-feedback.sh` + `northstar feedback n5` + doctor
4. **WS3** — Hermetic tests from checked-in N4 LATEST; security locks
5. **WS4** — ADR-096, CHANGELOG, VERSION 1.76.0, TESTING, INDEX

## Testing Strategy

Doctor fail-closed · unit ingest/suggest/locks · refuse apply · evidence packet

## Security Notes

Proposal-only; no weight apply; no secrets; path allowlist for N4 report input.

## Rollback Plan

Tag `rollback/pre-n5-skill-routing-feedback`; omit `feedback n5`; N4 unchanged.

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 8 |
| Failed validation cycles | 3 |
| Cost | Low (hermetic; no paid GPU) |
| Ledger | `.agent/budgets/n5-skill-routing-feedback.md` *(after approval)* |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve** / **proceed with N5 plan** (or revise open questions) to unlock WS0–WS4.

> Note: “proceed with N5” after #243 is treated as intent to start the track; **this document** still needs an explicit approve before product/harness code lands.
