# Implementation Plan — M33 / B5 Precision ledger (Skill/reviewer reputation)

> Archive mirror of root `IMPLEMENTATION_PLAN.md` (plan id `b5-precision-ledger`).


## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING_APPROVAL** |
| Plan ID | `b5-precision-ledger` |
| Supersedes | `b4-repair-loop` (CLOSED — shipped as v1.35.0 / M32 / B4) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.35.0` / `origin/main` (M32 merged, PR #156 / #157) |
| Prepared | 2026-09-15 |
| Approved | — |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track B / **B5**; design `docs/design/NorthStar_Code_Reviewer.md` reputation section |
| Linear | [OVA-49](https://linear.app/ovaltechnologysolutions/issue/OVA-49) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.36.0** |
| Rollback tag | `rollback/pre-b5-precision-ledger` (create after approval) |
| Branch | (create after approval) `cursor/m33-b5-precision-ledger-3b10` |
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

1. **Plan-gated** — implementation starts only after Captain approves this document.
2. **Ledger schema** — versioned `precision-ledger` (or equivalent) aggregating findings by `skill_slug` / specialist / heuristic key with accepted, rejected, deferred, precision rate, and source run ids.
3. **Aggregator CLI** — hermetic `northstar precision …` (or `outcomes precision`) reads finding-outcome evidence + Experience and writes ledger + dashboard artifacts under `.agent/evidence/precision/<run-id>/`.
4. **Dashboard artifact** — markdown and/or JSON summary showing per-Skill precision (accepted / (accepted+rejected)), finding counts, and last-updated — readable in evidence and optionally mirrored as Experience lessons.
5. **Invocation-priority proposal (optional flag)** — emit RoutingProposal-style proposal to raise/lower specialist invocation priority from precision floors/ceilings; **never auto-apply**.
6. **Refuse paths** — empty outcomes, unknown skill keys, and insufficient sample size do not invent precision; doctor + unit tests cover these.
7. **Doctor + unit tests** — hermetic coverage for aggregate math, redaction, proposal-only flags.
8. **Docs** — ADR-050 (or next free), `docs/integrations/` note, Skill cross-links (`code-reviewer`).
9. **Memory** — DECISIONS / PROGRESS / CHANGELOG / VERSION → **1.36.0**.
10. **Fixture proof** — re-use M31 triage fixtures (and/or M28 bitcoin-style demo outcomes) to produce a non-empty precision dashboard in evidence.

## Architecture (proposed)

```
finding-outcome evidence (M31) + Experience lessons
        │
        ▼
northstar precision aggregate [--emit-priority-proposal]
        │
        ├─ precision-ledger.json (durable roll-up)
        ├─ dashboard.md / dashboard.json (evidence)
        ├─ optional Experience lesson(s) summarizing precision
        └─ optional RoutingProposal (auto_apply=false) for invocation priority
```

## Implementation steps (after approval only)

1. Create rollback tag `rollback/pre-b5-precision-ledger`.
2. Author precision-ledger schema + aggregator module.
3. Wire CLI + doctor checks.
4. Optional priority-proposal emitter (proposal-only).
5. Hermetic tests + fixture dashboard evidence.
6. Docs + ADR + VERSION 1.36.0.
7. Open PR to `main`; Captain merge → tag **v1.36.0**.

## Validation plan

| Layer | How |
|---|---|
| Static | doctor.sh |
| Unit | precision math; empty/insufficient sample refuse; proposal flags |
| Integration | M31 fixture outcomes → ledger + dashboard evidence |
| Security | redaction; no secret commit; no network default |
| Rollback | revert PR / reset to rollback tag |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Silent demotion of useful Skills | Proposal-only; Captain apply separate |
| Overfitting on tiny samples | Minimum sample floor before proposals |
| Scope into Learning Loop ledger rewrite | Explicit non-goal; review-outcome precision only |
| Confusing deferred with FP | Deferred excluded from precision denominator (accepted+rejected only) |

## Budget

After approval: `.agent/budgets/b5-precision-ledger.md`

Soft stop: AC + tests + evidence + PR. Hard stop: no auto-apply reputation; no model-in-CI default; no Linear approval origin.

## Rollback

1. Revert the B5 PR or reset to rollback tag.
2. Confirm M31 outcomes + M32 repair still work.
3. VERSION/CHANGELOG note if tag already cut.

## Open questions (for Captain, non-blocking)

1. Prefer CLI as `northstar precision aggregate` vs `northstar outcomes precision`?
2. Minimum sample size before emitting a priority proposal (suggested default: **5** decided findings)?
3. Proceed with B5 now **and** continue Learning Run / OVA-45 retain in parallel?

## Approval gate

**AWAITING_APPROVAL** — reply with:

`I approve IMPLEMENTATION_PLAN.md for b5-precision-ledger`

No product implementation until that utterance (or equivalent explicit approval) is recorded.
