# Implementation Plan — M31 Finding outcomes → Experience → RoutingProposal

## Metadata

| Field | Value |
|---|---|
| Status | **IMPLEMENTING** |
| Plan ID | `m31-finding-outcomes-experience` |
| Supersedes | `m30-github-draft-reviews` (CLOSED — shipped as v1.33.0 / M30) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.33.0` / `origin/main` (M30 merged, PR #149) |
| Prepared | 2026-09-15 |
| Approved | 2026-09-15 — Captain: “I approve IMPLEMENTATION_PLAN.md for m31-finding-outcomes-experience” |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track A / **A3** + backlog M31 |
| Product dry-run target | control fixtures + optional sandbox review triage |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.34.0** |
| Rollback tag | `rollback/pre-m31-finding-outcomes`  |
| Branch | `cursor/m31-finding-outcomes-3b10` |
| Issue | [#150](https://github.com/loganware05/captains-compass-cursor/issues/150) |
| Captain | Logan Ware |

## Captain locks (binding — carry forward + M31)

1. **Hermetic CI** — no model calls on the default path
2. **Skill slug** — `code-reviewer` unchanged
3. **Captain gate** — RoutingProposal / Skill confidence deltas are proposals only; never auto-apply
4. **Linear** — flight recorder only; never approval authority
5. **No auto-merge** — including repair PRs (B4 remains a separate plan)
6. **No silent scope into B4** — FIND→FIX repair loop is explicitly out of scope here
7. **Evidence truth** — outcomes must cite review run ids + finding ids under `.agent/evidence/`

## Request (Captain-level)

Proceed with **M31 — Finding outcomes → Experience → RoutingProposal**: after humans triage Code Reviewer verified findings (accept/reject / TP/FP), record durable Experience lessons and optionally emit a Captain-gated RoutingProposal that adjusts Skill/reviewer confidence — closing the review→learning loop from the roadmap.

## Problem statement

1. M27–M30 produce verified findings and optional draft reviews, but accepted/rejected outcomes are not yet stored as Experience.
2. Roadmap A3 exit: at least one Skill confidence delta **proposed** from review outcomes.
3. Without outcome memory, specialist emitters and Skill reputation cannot improve from real triage.

## Non-goals

- Auto-applying RoutingProposal / Skill weight changes
- FIND→FIX repair-loop automation (B4 / M32+)
- Webhook-driven auto-triage
- Model-generated lesson prose on the default path
- Changing Linear into an approval authority
- Precision dashboards UI (B5) — schema/evidence only if needed

## Acceptance criteria

1. **Outcome schema** — `orchestrator/schemas/finding-outcome.schema.json` (or equivalent) with fields at least: `run_id`, `finding_id`, `decision` (`accepted`|`rejected`|`deferred`), `label` (`tp`|`fp`|`unknown`), `skill`, `notes`, `captain_approval=false`.
2. **CLI / writer** — hermetic command or module to record outcomes from a completed review report + triage input (fixture JSON supported).
3. **Experience write** — accepted/rejected outcomes produce Experience lessons under the existing Experience store path; secrets redacted.
4. **RoutingProposal (optional)** — when enough outcomes exist for a Skill, emit a proposal artifact only (Captain-gated; never applied in this milestone).
5. **Doctor** — schema + module/script presence checks.
6. **Tests** — unit tests for schema, writer, Experience emit, proposal gate; no live network required.
7. **Evidence** — fixture triage run documented under `.agent/evidence/m31-finding-outcomes/`.
8. **Docs** — code-reviewer integration note + ADR-048; VERSION → **1.34.0**.
9. **Memory** — DECISIONS / PROGRESS / CHANGELOG updated.
10. Default review path unchanged: hermetic, no model, draft posting still opt-in.

## Architecture (proposed)

```
code-review report.json  +  triage outcomes.json
            │
            ▼
orchestrator/review/outcomes.py  →  finding-outcome.schema.json
            │
            ├─► Experience lesson(s)
            └─► RoutingProposal (optional, not applied)
```

## Implementation steps (after approval only)

1. Create rollback tag `rollback/pre-m31-finding-outcomes`.
2. Author outcome schema + writer module.
3. Wire Experience emit + optional RoutingProposal builder.
4. CLI/script + doctor checks.
5. Tests + fixture evidence.
6. Docs + ADR/PROGRESS/CHANGELOG/VERSION.
7. Open PR to `main`; Captain merge → tag **v1.34.0**.

## Validation plan

| Layer | How |
|---|---|
| Static | doctor.sh; schema validate outcomes |
| Unit | outcome parse; Experience write; proposal not auto-applied |
| Integration | fixture review report → outcomes → Experience artifacts |
| Security | redaction of tokens/notes |
| Rollback | revert PR / reset to rollback tag |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Auto-applying confidence changes | Hard non-goal; proposals only |
| Scope creep into repair loop | Explicit non-goal; separate plan for B4 |
| Noisy FP labels | Require finding_id + run_id; fixture tests |

## Budget

After approval: `.agent/budgets/m31-finding-outcomes-experience.md`

Soft stop: AC + tests + evidence + PR. Hard stop: no auto-apply; no B4 repair; no model-in-CI.

## Rollback

1. Revert the M31 PR or reset to rollback tag.
2. Confirm Code Reviewer + M30 draft posting still work.
3. VERSION/CHANGELOG note if tag already cut.

## Approval gate

**Captain approved this plan on 2026-09-15**
(`I approve IMPLEMENTATION_PLAN.md for m31-finding-outcomes-experience`).
Implementation proceeds on `cursor/m31-finding-outcomes-3b10` toward **v1.34.0**.

Locks confirmed:

- proposals only / no auto-apply
- no FIND→FIX in this milestone
- hermetic default path unchanged
- Linear never approves
