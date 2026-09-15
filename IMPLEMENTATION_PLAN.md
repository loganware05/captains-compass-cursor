# Implementation Plan — M32 / B4 Repair loop (FIND→PROVE→FIX→TEST→SUBMIT)

## Metadata

| Field | Value |
|---|---|
| Status | **SHIPPED** (via PR #156 / v1.35.0) |
| Plan ID | `b4-repair-loop` |
| Supersedes | `m31-finding-outcomes-experience` (CLOSED — shipped as v1.34.0 / M31 / A3) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.34.0` / `origin/main` (M31 merged, PR #152) |
| Prepared | 2026-09-15 |
| Approved | 2026-09-15 — Captain: “I approve the dispatch, I approve M31/ B4 plan” |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track B / **B4**; long-form `docs/plans/B4_REPAIR_LOOP.md` |
| Linear | [OVA-48](https://linear.app/ovaltechnologysolutions/issue/OVA-48) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.35.0** |
| Rollback tag | `rollback/pre-b4-repair-loop` (create after approval) |
| Branch | `cursor/m32-b4-repair-loop-05fd` (merged); alternate PR #157 resolved onto main |
| Issue | [#154](https://github.com/loganware05/captains-compass-cursor/issues/154) |
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
9. **Skill slug** — `code-reviewer` unchanged
10. **Finding outcomes remain proposal-gated** — M31 RoutingProposal apply stays a separate Captain action

## Request (Captain-level)

Approve planning for **M32 / B4 — Repair loop**: after Code Reviewer produces verified findings, spawn a supervised FIND→PROVE→FIX→TEST→SUBMIT child workflow via agent routing, ending in a human-reviewed PR (never auto-merge).

## Problem statement

1. M27–M31 ship detect→verify→(optional draft post)→finding outcomes / Experience. Humans still open fix PRs by hand.
2. Roadmap B4 exit: *one supervised repair PR from a verified finding*.
3. Without gates, repair automation could amplify false positives or merge unsafe changes.

## Non-goals

- Auto-merge / auto-approve of repair PRs
- Webhook-driven repair on every PR
- Repairing unverified or discarded findings
- Changing Linear approval semantics
- Auto-applying M31 RoutingProposal / Skill confidence deltas
- Replacing Code Reviewer Skill slug

## Dependencies

| Dep | Status |
|---|---|
| B3 — GitHub draft reviews (M30) | **Done** (v1.33.0) |
| A3 — Review-informed learning (M31 finding-outcomes) | **Done** (v1.34.0) |
| Agent router wakeability (M25/M26) | **Done** |
| Active Learning Run routing pattern | In progress (NS-SKILL-003 / OVA-45) — may proceed in parallel |

## Acceptance criteria

1. **Plan-gated** — implementation starts only after Captain approves this document.
2. **Finding intake** — CLI/module accepts a verified finding id/path from a Code Reviewer report (`verified=true`, severity ≥ floor).
3. **PROVE step** — re-check or cite existing verify evidence before FIX; refuse if finding no longer verified.
4. **Child task packet** — writes dispatch packet + objective JSON for agent router (M26 probe optional but preferred).
5. **FIX→TEST** — bounded code change + tests in allowlisted repo; evidence under `.agent/evidence/repair/<run-id>/`.
6. **SUBMIT** — opens draft PR (or prepares branch) with finding link + rollback notes; **no auto-merge**.
7. **Captain stop gates** — pause before FIX dispatch and before SUBMIT merge, unless Captain pre-authorizes in repo evidence.
8. **Doctor + unit tests** — hermetic coverage for refuse paths (unverified finding, expired agent, non-allowlisted repo).
9. **Docs** — ADR-049 (or next free), `docs/integrations/` note, Skill cross-links (`code-reviewer`, `review-fix-loop` if present).
10. **Memory** — DECISIONS / PROGRESS / CHANGELOG / VERSION → **1.35.0**.
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

## Implementation steps (after approval only)

1. Create rollback tag `rollback/pre-b4-repair-loop`.
2. Author repair intake + PROVE refuse paths.
3. Wire agent-router dispatch packet (Captain-gated).
4. Bounded FIX→TEST evidence writer + draft PR submit (no auto-merge).
5. Doctor + hermetic tests + sandbox proof.
6. Docs + ADR + VERSION 1.35.0.
7. Open PR to `main`; Captain merge → tag **v1.35.0**.

## Validation plan

| Layer | How |
|---|---|
| Static | doctor.sh |
| Unit | unverified refuse; allowlist refuse; no auto-merge |
| Integration | fixture verified finding → dry-run repair evidence |
| Security | redaction; token hygiene; no secret commit |
| Rollback | revert PR / reset to rollback tag |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Amplifying FP findings | Verified-only + severity floor + PROVE re-check |
| Accidental merge | Hard non-goal; draft PR only |
| Scope into auto-apply reputation | Explicit non-goal; M31 apply stays separate |

## Budget

After approval: `.agent/budgets/b4-repair-loop.md`

Soft stop: AC + tests + evidence + PR. Hard stop: no auto-merge; no unverified repair; no model-in-CI default.

## Rollback

1. Revert the B4 PR or reset to rollback tag.
2. Confirm Code Reviewer + M31 outcomes still work.
3. VERSION/CHANGELOG note if tag already cut.

## Open questions (resolved)

1. Prefer repair CLI as `northstar repair …` — **yes** (shipped).
2. First proof target: **sandbox fixture** dry-run (this PR); live product finding later.
3. Proceed with B4 now **and** finish Learning Run / OVA-45 in parallel — Captain approved both.

## Approval gate

**APPROVED** 2026-09-15 — Captain: “I approve the dispatch, I approve M31/ B4 plan”.

Implementation in progress on `cursor/m32-b4-repair-loop-05fd`. Rollback tag: `rollback/pre-b4-repair-loop`.
