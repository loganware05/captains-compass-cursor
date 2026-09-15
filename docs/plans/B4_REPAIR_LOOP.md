# Implementation Plan — B4 Repair loop (FIND→PROVE→FIX→TEST→SUBMIT)

> **Not the active root `IMPLEMENTATION_PLAN.md`.**  
> Active M31 is **Finding outcomes → Experience → RoutingProposal**
> (`m31-finding-outcomes-experience`, issue #150 / PR #152).  
> This document is a **draft** for roadmap **B4** (queued after A3).

## Metadata

| Field | Value |
|---|---|
| Status | **DRAFT — awaiting Captain approval** |
| Plan ID | `b4-repair-loop` |
| Supersedes | n/a (parallel track to A3 / M31 finding-outcomes) |
| Product | **NorthStar** |
| Baseline | `v1.33.0` / `origin/main` (M30 merged); prefer after M31 A3 lands |
| Prepared | 2026-09-15 |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track B / **B4** |
| Linear | [OVA-48](https://linear.app/ovaltechnologysolutions/issue/OVA-48) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **TBD** (after M31 / v1.34.0 — do not claim M31 numbering) |
| Rollback tag | `rollback/pre-b4-repair-loop` (create after approval) |
| Captain | Logan Ware |
| Queue | `.agent/queues/captain-objectives-2026-09-15.md` item 3 |

## Captain locks (binding)

1. **Never auto-merge** — repair PRs stay human-reviewed
2. **Captain plan gate** — no product implementation until this plan is explicitly approved
3. **Verified findings only** — spawn repair work only from Code Reviewer **verified** findings (not unverified/discarded)
4. **Sandbox / allowlisted repos first** — prove on `captain-compass-sandbox` before bitcoin-data-collector
5. **Agent router + Learning Loop** — child tasks use `northstar.agent_router.v1` + M26 wakeability; fail closed on expired pins
6. **Linear records only** — never treat Linear as approval origin
7. **Hermetic CI** — default tests/doctor remain network-free
8. **`approved_for_execution` stays false** for Stars TI candidates

## Request (Captain-level)

Approve planning for **B4 — Repair loop**: after Code Reviewer produces verified findings, spawn a supervised FIND→PROVE→FIX→TEST→SUBMIT child workflow via agent routing, ending in a human-reviewed PR (never auto-merge).

## Problem statement

1. M27–M30 ship detect→verify→(optional draft post). Humans still open fix PRs by hand.
2. Roadmap B4 exit: *one supervised repair PR from a verified finding*.
3. Without gates, repair automation could amplify false positives or merge unsafe changes.

## Non-goals

- Auto-merge / auto-approve of repair PRs
- Webhook-driven repair on every PR
- Repairing unverified or discarded findings
- Changing Linear approval semantics
- Full A3 precision ledger / reputation dashboards (may land partial bridge only)
- Replacing Code Reviewer Skill slug
- Claiming the M31 / v1.34.0 slot (reserved for finding-outcomes A3)

## Dependencies

| Dep | Status |
|---|---|
| B3 — GitHub draft reviews (M30) | **Done** (v1.33.0) |
| A3 — Review-informed learning (M31 finding-outcomes) | **In progress** — PR #152 |
| Agent router wakeability (M25/M26) | **Done** |
| Active Learning Run routing pattern | In progress (NS-SKILL-003 / OVA-45) |

## Acceptance criteria

1. **Plan-gated** — implementation starts only after Captain approves this document.
2. **Finding intake** — CLI/module accepts a verified finding id/path from a Code Reviewer report (`verified=true`, severity ≥ floor).
3. **PROVE step** — re-check or cite existing verify evidence before FIX; refuse if finding no longer verified.
4. **Child task packet** — writes dispatch packet + objective JSON for agent router (M26 probe optional but preferred).
5. **FIX→TEST** — bounded code change + tests in allowlisted repo; evidence under `.agent/evidence/repair/<run-id>/`.
6. **SUBMIT** — opens draft PR (or prepares branch) with finding link + rollback notes; **no auto-merge**.
7. **Captain stop gates** — pause before FIX dispatch and before SUBMIT merge, unless Captain pre-authorizes in repo evidence.
8. **Doctor + unit tests** — hermetic coverage for refuse paths (unverified finding, expired agent, non-allowlisted repo).
9. **Docs** — new ADR (not ADR-048 — that is M31 finding-outcomes), `docs/integrations/` note, Skill cross-links (`code-reviewer`, `review-fix-loop` if present).
10. **Memory** — DECISIONS / PROGRESS / CHANGELOG / VERSION (version TBD after M31).
11. **Sandbox proof** — one supervised repair PR (or dry-run evidence) on `captain-compass-sandbox`.

## Architecture (proposed)

```
code-review report.json (verified finding)
        │
        ▼
northstar repair start --finding <id> [--cloud-agents-json]
        │
        ├─ PROVE (re-verify / refuse)
        │
        ├─ route_agents (M26 probe) → dispatch packet
        │     └─ stop unless Captain authorizes dispatch
        │
        ├─ FIX + TEST (bounded) → evidence
        │
        └─ SUBMIT draft PR → stop (never auto-merge)
```

## Rollback

1. Tag `rollback/pre-b4-repair-loop` at approval time.
2. Revert B4 PR(s); leave M31 finding-outcomes intact.
3. Disable repair CLI entrypoints via feature flag / docs “do not use” if partial land.

## Open questions for Captain

1. Prefer repair CLI as `northstar repair …` vs Skill-only procedure?
2. First proof target: sandbox fixture finding vs live bitcoin-data-collector verified finding?
3. Is M31 finding-outcomes (Experience + proposal-only RoutingProposal) enough to start B4, or must applied Skill reputation land first?

## Approval

Reply with an explicit approval (e.g. `I approve docs/plans/B4_REPAIR_LOOP.md` / `I approve the B4 plan`) to authorize implementation.  
Do **not** use `I approve M31` for this document — M31 refers to finding-outcomes.
