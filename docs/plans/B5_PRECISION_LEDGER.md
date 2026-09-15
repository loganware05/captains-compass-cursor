# Implementation Plan — M33 / B5 Precision ledger (Skill/reviewer reputation)

> Archive mirror of root `IMPLEMENTATION_PLAN.md` (plan id `b5-precision-ledger`).


## Metadata

| Field | Value |
|---|---|
| Status | **SHIPPED** (via this PR / v1.36.0) |
| Plan ID | `b5-precision-ledger` |
| Supersedes | `b4-repair-loop` (CLOSED — shipped as v1.35.0 / M32 / B4) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.35.0` / `origin/main` (M32 merged, PR #156 / #157) |
| Prepared | 2026-09-15 |
| Approved | 2026-09-15 — Captain: “I approve IMPLEMENTATION_PLAN.md for b5-precision-ledger” |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track B / **B5**; design `docs/design/NorthStar_Code_Reviewer.md` reputation section |
| Linear | [OVA-49](https://linear.app/ovaltechnologysolutions/issue/OVA-49) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.36.0** |
| Rollback tag | `rollback/pre-b5-precision-ledger` |
| Branch | `cursor/m33-b5-precision-ledger-3b10` |
| Issue | [#158](https://github.com/loganware05/captains-compass-cursor/issues/158) |
| Captain | Logan Ware |
| Queue | `.agent/queues/captain-objectives-2026-09-15.md` |

## Captain locks (binding)

1. **Captain plan gate** — no product implementation until this plan is explicitly approved
2. **No silent reputation mutation** — precision updates never auto-apply Skill confidence or demote Skills without Captain action
3. **Proposal-only priority gates** — any invocation-priority / confidence delta is `auto_apply=false` / `captain_approved=false` until a separate Captain apply
4. **Outcomes remain non-approval** — finding outcomes never originate Captain approval (ADR-048)
5. **Linear records only** — never treat Linear as approval origin
6. **Hermetic CI** — default tests/doctor remain network-free
7. **`approved_for_execution` stays false** for Stars TI candidates
8. **Skill slug** — `code-reviewer` unchanged
9. **Never auto-merge** — repair / review GitHub surfaces stay human-reviewed
10. **Sandbox / fixture-first** — prove ledger + dashboard on control fixtures before product-repo live triage

## Request (Captain-level)

Approve planning for **M33 / B5 — Precision ledger**: aggregate Code Reviewer accepted/rejected finding outcomes into a durable precision ledger, emit evidence/Experience dashboards, and optionally propose (never auto-apply) specialist/Skill invocation-priority adjustments.

## Problem statement

1. M31 stores per-finding triage (accepted/rejected/deferred) as Experience + optional RoutingProposal, but there is **no roll-up** of precision by Skill / specialist / heuristic over time.
2. Roadmap B5 exit: *Precision dashboards in evidence/Experience*.
3. Design intent: high-precision Skills rise in invocation priority; low-precision ones require improvement — without building a separate SaaS or silently mutating reputation.

## Non-goals

- Auto-applying confidence / priority changes without Captain action
- Auto-retiring or auto-demoting Skills
- Changing Linear approval semantics
- Replacing the Skills Learning Loop ledger (M24) — B5 complements it with **review-outcome** precision
- Expanding FIND→FIX live repair beyond B4 packet MVP
- Changing Skill slug `code-reviewer`
- Webhooks or model-in-CI default path

## Dependencies

| Dep | Status |
|---|---|
| A3 — Review-informed learning (M31 finding-outcomes) | **Done** (v1.34.0) |
| B4 — Repair loop packet MVP (M32) | **Done** (v1.35.0) |
| Experience store / `write_experience` | **Done** |
| RoutingProposal proposal-only path | **Done** (M31) |

## Acceptance criteria

1. **Plan-gated** — implementation starts only after Captain approves this document. ✅
2. **Ledger schema** — versioned `precision-ledger` aggregating findings by skill key. ✅
3. **Aggregator CLI** — `northstar precision aggregate` / `aggregate-precision-ledger.sh`. ✅
4. **Dashboard artifact** — markdown + JSON under `.agent/evidence/precision/<id>/`. ✅
5. **Invocation-priority proposal (optional flag)** — proposal-only; never auto-apply. ✅
6. **Refuse paths** — empty outcomes, empty skill, insufficient sample. ✅
7. **Doctor + unit tests** — hermetic coverage. ✅
8. **Docs** — ADR-050, integrations, Skill cross-links. ✅
9. **Memory** — DECISIONS / PROGRESS / CHANGELOG / VERSION → **1.36.0**. ✅
10. **Fixture proof** — non-empty precision dashboard in evidence. ✅

## Architecture (shipped)

```
finding-outcome evidence (M31)
        │
        ▼
northstar precision aggregate [--emit-priority-proposal]
        │
        ├─ precision-ledger.json
        ├─ dashboard.md / dashboard.json
        ├─ optional Experience lesson
        └─ optional RoutingProposal (auto_apply=false)
```

## Validation

| Layer | Result |
|---|---|
| Static | doctor.sh passed |
| Unit | `test_m33_b5_precision_ledger.py` passed |
| Integration | fixture → ledger + dashboard + proposal evidence |
| Security | redaction; proposal-only; no secret commit |
| Rollback | `rollback/pre-b5-precision-ledger` |

## Budget

`.agent/budgets/b5-precision-ledger.md` — soft stop met; hard stops held.

## Rollback

1. Revert this PR or reset to `rollback/pre-b5-precision-ledger`.
2. Confirm M31 outcomes + M32 repair still work.
3. VERSION/CHANGELOG note if tag already cut.

## Open questions (resolved)

1. CLI as `northstar precision aggregate` — **yes**.
2. Minimum sample for priority proposal — **5** (default).
3. Parallel with Learning Run / OVA-45 — **yes** (unchanged).

## Approval gate

**APPROVED** 2026-09-15 — Captain: “I approve IMPLEMENTATION_PLAN.md for b5-precision-ledger”.

Shipped on `cursor/m33-b5-precision-ledger-3b10`. Rollback tag: `rollback/pre-b5-precision-ledger`.
