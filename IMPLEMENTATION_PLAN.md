# Implementation Plan — M50 / Policy · Instruction Promotion Lifecycle

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m50-policy-promotion-lifecycle` |
| Approved | 2026-10-11 — Captain: "I approve" (accepts recommended decisions 1–6) |
| Linear | [OVA-66](https://linear.app/ovaltechnologysolutions/issue/OVA-66/m50-policy-instruction-promotion-lifecycle-v1550) · Milestone **M50 — Policy / Instruction Promotion Lifecycle** |
| Spec source | [Notion: Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M50 section) |
| Notion plan mirror | [M50 Implementation Plan](https://app.notion.com/p/3f6e6a901c4381b4b7b3f04d2f848aa9) |
| Linear project | [NorthStar Behavioral Intelligence Loop](https://linear.app/ovaltechnologysolutions/project/northstar-behavioral-intelligence-loop-e24174b3f1ef) (P-OVA-4) |
| Prerequisite | **M49 shipped** — PR [#187](https://github.com/loganware05/captains-compass-cursor/pull/187) → v1.49.0; **AHF-P06 merged** — PR [#192](https://github.com/loganware05/captains-compass-cursor/pull/192) → **v1.54.0** @ `dad671f` |
| Supersedes | Completed plan `ahf-p06-behavioral-coupling` (research track; live execution still denied) |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.54.0** @ `dad671f` |
| Prepared | 2026-10-11 |
| Proposed release | **v1.55.0** (v1.50.0 already claimed by AHF-P01) |
| Rollback | Tag `rollback/pre-m50-policy-promotion` @ `dad671f` |
| Proposed branch | `feature/OVA-66-m50-policy-promotion-lifecycle` |
| Capability plan | `.agent/plans/m50-policy-promotion-lifecycle/` |
| Captain | Logan Ware |

## Request

Continue the [NorthStar Behavioral Intelligence Loop](https://linear.app/ovaltechnologysolutions/project/northstar-behavioral-intelligence-loop-e24174b3f1ef)
after M46–M49 and the AHF research track. Establish **M50 Policy / Instruction
Promotion Lifecycle**: a governed state machine from candidate guidance through
sandbox eval, shadow, Captain approval, Active, and Proven — without silent
authority mutation.

## Current state (evidence)

| Track | Status |
|---|---|
| M46–M49 Behavior Loop | Shipped on `main` (v1.46.0–v1.49.0); Linear OVA-61 still stale In Progress |
| AHF-P01–P06 | Shipped on `main` through **v1.54.0** (#192); readiness **deny** live execution |
| M50 | Linear milestone exists (0%); **no issue / no plan** until this document |
| M51 Project Overseer | Deferred until M50 lands |
| Repo memory | `PROGRESS.md` / `PROJECT_CONTEXT.md` still describe AHF-P06 as active — refresh in M50 docs slice |

## Problem Statement

M48 stores instructions as `draft|candidate` only. M49 can prove non-regression
via prompt-eval reports. NorthStar still cannot:

1. Advance an instruction/Policy through sandbox → shadow → Captain-approved → Active → Proven
2. Require M49 evidence (and related provenance) before promotion
3. Run **shadow mode** that records what Active policy *would* change without applying it
4. Expose a stable operator surface for promotion with dual enable gates + `--captain-approved`
5. Keep `approved_for_execution: false` / `authority_mutation: false` through every state

Without M50, candidates remain forever inert or risk ad-hoc activation outside
the governed loop.

## Desired Outcome

```
M47 candidates → M48 draft/candidate instructions
  → M49 prompt-eval report (non_regression=pass)
  → promote sandbox_evaluated → shadowed (would-have record)
  → Captain --captain-approved → active → proven
  → northstar policy …
  → evidence under .agent/evidence/m50-policy-promotion-lifecycle/
```

No path may auto-write `.cursor/rules|skills|agents`, mutate Skills/routing,
grant trade/execution authority, or set `approved_for_execution: true`.

## Decision Summary

| Principle | Implication |
|---|---|
| Skills ≠ Policies | Promotion lifecycle for **behavior** (instructions/Policies), not TI Skills |
| Mirror skill-lifecycle | Explicit stages + evidence + `--captain-approved` for mutating stages |
| Shadow before Active | Persist would-have-changed compose diffs; never live-apply from shadow |
| M49 gate | `sandbox_evaluated` requires referenced prompt-eval report with `non_regression=pass` |
| Active ≠ `.cursor/` write | Active means eligible for compose-include under apply gate; materialize is proposal-only |
| Dual enable gate | Env flag (default off) **and** explicit CLI |
| Fail closed | Illegal transitions / missing evidence → deny; never mutate authority |
| Version | **v1.55.0** (avoid colliding with AHF v1.50–v1.54) |

## Resolved Decisions (Captain — 2026-10-11)

| # | Decision |
|---|---|
| 1 | Top-level **`northstar policy`** |
| 2 | New **`COMPASS_POLICY_PROMOTE_ENABLED`** (default off) |
| 3 | Active = compose-eligible only under **`COMPASS_POLICY_APPLY_ENABLED`** |
| 4 | Materialize **proposals only** (no auto `.cursor/` copy) |
| 5 | Proven threshold **≥2** (overrideable via env) |
| 6 | Release **v1.55.0** |

## Approval Record

Captain Logan Ware — 2026-10-11 — "I approve" (recommended decisions 1–6 accepted).

## Scope

### In (M50)

1. Extend instruction `approval_state` (or introduce Policy wrapper) with lifecycle:
   `draft → candidate → sandbox_evaluated → shadowed → approved → active → proven`
   (plus terminal `retired` optional)
2. Schemas: `behavior-policy.schema.json` + `policy-promotion-event.schema.json` + `shadow-report.schema.json` — fail-closed (`approved_for_execution: false`, `authority_mutation: false`)
3. Package `orchestrator/behavior/policy/` — state machine, gates, shadow compare, materialize proposal, service
4. Persist under `.agent/evaluations/behavior/policies/` (+ `shadow/` + `events/` + `materialize-proposals/`)
5. Promotion gates:
   - → `sandbox_evaluated`: M49 report id with `non_regression=pass`
   - → `shadowed`: write shadow report (baseline compose vs candidate/active-would-be)
   - → `approved` / `active` / `proven`: `--captain-approved` required
   - → `proven`: ≥N successful M46 evaluations referencing policy / bundle hash
6. `northstar policy` CLI: `list`, `show`, `promote`, `shadow`, `materialize-proposal`, `export` *(exact verbs may trim)*
7. Enable gates: `COMPASS_POLICY_PROMOTE_ENABLED` (+ optional `COMPASS_POLICY_APPLY_ENABLED` for compose-include)
8. Wire composer selection: Active policies includable only when apply flag set; proposals still excluded from observe-only evaluate path
9. Hermetic fixtures + unit/integration tests
10. Docs: ADR-072, TESTING, PROGRESS, PROJECT_CONTEXT, CHANGELOG, VERSION → 1.55.0
11. Evidence under `.agent/evidence/m50-policy-promotion-lifecycle/`
12. Doctor smoke: fail-closed when promote flag unset
13. Linear hygiene: mark OVA-61 Done; attach this plan to new M50 issue

### Out (Non-Goals)

- Auto-writing or merging into `.cursor/rules|skills|agents`
- Auto-setting `approved_for_execution: true` (including AHF readiness)
- Project Overseer (`northstar status…`) — **M51**
- Live Jev/LLM required for CI
- Mutating Skills, TI candidate lifecycle, routing weights, or merge authority
- Database / Prisma / frontend
- Closing Linear project epic without Captain confirmation

## Proposed Architecture

```
scripts/northstar policy …
        │
        ▼
scripts/run-policy.sh
        │
        ▼
orchestrator/behavior/policy/
  states.py / gates.py / shadow.py / promote.py / materialize.py / service.py
        │
        ├─► M48 instruction store (approval_state transitions)
        ├─► M49 prompt-eval reports (sandbox gate)
        ├─► M46 behavior ledger (proven gate)
        └─► composer (apply-flag gated Active include)
        │
        ▼
.agent/evaluations/behavior/policies/
  <policy-id>.json
  shadow/<shadow-id>.json
  events/<event-id>.json
  materialize-proposals/<policy-id>/
(+ evidence under .agent/evidence/m50-policy-promotion-lifecycle/)
```

### Lifecycle (governed)

```
Observed (M46/M47)
  → Candidate (M48 draft/candidate)
  → Sandbox Evaluated (M49 non_regression=pass)
  → Shadowed (would-have record; applied=false)
  → Captain Approved (--captain-approved)
  → Active (compose-eligible under apply flag)
  → Proven (≥N successful evaluations)
```

Illegal transitions fail closed. Shadow never sets `applied: true`.

## Capability / Agent Plan (adjusted)

Capability planner emitted a generic frontend-heavy graph; **override for this
control-repo milestone**:

| Task | Profile | Notes |
|---|---|---|
| discovery | `repository-scout` | Confirm M48/M49 store + CLI seams |
| architecture | `architecture-agent` | Schema + state machine + gates |
| implementation | `implementation-agent` | `orchestrator/behavior/policy/` + CLI (no UI) |
| validation | `test-engineer` | Hermetic unit/integration + doctor |
| documentation | `documentation-agent` | ADR/PROGRESS/VERSION/Linear |

Machine artifacts: `.agent/plans/m50-policy-promotion-lifecycle/`.

## Files to Add / Modify

### Add

| Path | Purpose |
|---|---|
| `orchestrator/behavior/policy/` | Lifecycle package |
| `orchestrator/schemas/behavior-policy.schema.json` | Policy object |
| `orchestrator/schemas/policy-promotion-event.schema.json` | Transition events |
| `orchestrator/schemas/shadow-report.schema.json` | Shadow would-have report |
| `scripts/run-policy.sh` | Enable-gated runner |
| `tests/fixtures/behavior/policy/` | Hermetic fixtures |
| `tests/orchestrator/test_m50_policy_promotion.py` | Tests |
| `docs/plans/M50_POLICY_PROMOTION_LIFECYCLE.md` | Plan archive |
| `.agent/budgets/m50-policy-promotion-lifecycle.md` | Autonomy budget |
| `.agent/evidence/m50-policy-promotion-lifecycle/` | Validation evidence |

### Modify (thin)

| Path | Change |
|---|---|
| `orchestrator/schemas/instruction.schema.json` | Extend `approval_state` enum (or keep instruction states and map via Policy wrapper) |
| `orchestrator/behavior/instructions/store.py` / `composer.py` | Controlled Active include + transition helpers |
| `orchestrator/behavior/enabled.py` | Promote / apply gates |
| `scripts/northstar` | Dispatch `policy` |
| `scripts/doctor.sh` | Fail-closed smoke |
| `orchestrator/schemas/validate.py` | Register new schemas |
| `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `PROJECT_CONTEXT.md`, `DECISIONS.md`, `VERSION` | M50 docs/release |

### Explicit non-touch

- No AHF live-execution enablement
- No M51 Project Overseer CLI
- No live provider keys in fixtures
- No silent Linear epic close

## Acceptance Criteria

- [x] Lifecycle transitions enforce evidence gates and `--captain-approved` where required
- [x] Shadow reports persist would-have compose diffs with `applied: false`
- [x] Schemas reject `approved_for_execution: true` / `authority_mutation: true`
- [x] `northstar policy` requires enable flag + explicit CLI
- [x] Active does not write `.cursor/`; materialize is proposal-only
- [x] Composer Active-include requires apply flag; evaluate path remains observe-only for proposals
- [x] M46–M49 suites still pass; doctor green
- [x] Evidence + ADR-072 + VERSION 1.55.0
- [x] Linear M50 issue linked; OVA-61 marked Done

## Test Matrix

| Layer | Coverage |
|---|---|
| Unit | Illegal transitions, missing M49 evidence, shadow applied=false, enable gates |
| Integration | CLI promote/shadow/materialize against fixtures |
| Regression | M46/M47/M48/M49 + AHF-P06 readiness deny unchanged |
| Security | No `.cursor/` writes; fail-closed gates; redaction |
| Doctor | Flag unset → policy promote unavailable |

## Rollback Plan

1. Tag `rollback/pre-m50-policy-promotion` @ `dad671f` after approval
2. Revert M50 PR / reset to tag
3. Remove `.agent/evaluations/behavior/policies/` artifacts if needed (non-canonical operator state)
4. VERSION / docs roll back with the revert

## Autonomy Budget

| Limit | Value |
|---|---|
| Max iterations | 8 |
| Max wall time | 4 hours |
| Stop on | Illegal authority mutation, failing security invariants, budget exhaustion |

Track in `.agent/budgets/m50-policy-promotion-lifecycle.md`.

## Security Considerations

- Dual enable gates + Captain flag for Active/Proven
- Fail closed on malformed evidence / missing prompt-eval
- Never commit secrets; redact instruction bodies in exports as M48 does
- Shadow and materialize are evidence/proposal only

## Approval Boundary

**Approved.** Implementation may proceed on `feature/OVA-66-m50-policy-promotion-lifecycle`
with rollback `rollback/pre-m50-policy-promotion` @ `dad671f`.
