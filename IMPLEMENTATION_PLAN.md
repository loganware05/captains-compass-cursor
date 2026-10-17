# Implementation Plan — C4 Cognitive Core Adaptive Development Loop

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `c4-cognitive-core-adaptive-loop` |
| Issue | [#208](https://github.com/loganware05/captains-compass-cursor/issues/208) |
| Notion | [Cognitive Core — C4 Adaptive Development Loop](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.62.0** @ `28ff856` (C3 merged #207) |
| Branch | *(create after approval)* `cursor/208-c4-adaptive-loop-64df` |
| Rollback | *(create after approval)* `rollback/pre-c4-cognitive-core-adaptive-loop` |
| Release | **v1.63.0** (proposed) |
| Captain | Logan Ware |
| Created | 2026-10-17 |

## Approval record

| Field | Value |
|---|---|
| Approved by | *(pending)* |
| Approval date | *(pending)* |
| Notes | Post-merge continuation after C3 (#207). Implementation must not begin until Captain explicitly approves this plan. |

## Request

Ship Cognitive Core **C4 — Adaptive Development Loop**: an idempotent, feature-gated controller that connects existing planning, C1–C3 Cognitive Core surfaces, ExecutionRun/Experience telemetry, Behavior Loop evaluation/pattern scan, and Skill Learning Loop draft paths into one lifecycle (`cycle begin|checkpoint|close` + `learning review`). Automate evidence capture and proposal generation only — never promotion, merge, or authority expansion.

## Problem Statement

Operators already have brain sync/context, difficulty assessment, `record-execution-run`, behavior evaluate/learn, and skill-learning drafts as separate surfaces. Notion Adaptive Intelligence requires a single resumable cycle that begins with sync + assess + plan artifacts, checkpoints actual vs estimated difficulty with tool/test/cost traces, and closes into Experiences + Captain Learning Review without changing promotion gates.

## Desired Outcome

```bash
COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar cycle begin --objective "…" --repo .

COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar cycle checkpoint --execution-id <id>

COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar cycle close --execution-id <id>

COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar learning review --repo .
```

Returns schema-validated JSON for cycle state and Learning Review packets. Always `approved_for_execution: false` / `authority_mutation: false`. Fail-closed without `COMPASS_CYCLE_ENABLED=1`. Idempotent and SHA-aware; resumable after interruption.

### Lifecycle (Notion)

| Phase | Actions (compose existing; do not reimplement) |
|---|---|
| **Begin** | Optional brain sync; resolve capabilities; C3 assess; retrieve similar Experiences; identify Skill gaps; draft plan/task-graph/manifest/budget/validation pointers |
| **Checkpoint** | Record task outcome, retries, tool/test traces, Skills/instructions/model used, cost; compare vs original difficulty; update remaining-work forecast **without** expanding approved scope |
| **Close** | Finalize ExecutionRun; create Experiences; behavior evaluation + pattern scan; Skill performance evidence; draft Skill/instruction/policy improvements; sandbox/prompt-eval hooks when available; emit Captain Learning Review |
| **Learning review** | Aggregate open draft proposals + evidence links for Captain decision — advisory only |

## Acceptance Criteria

- [ ] Gated `northstar cycle begin|checkpoint|close` and `learning review` (fail-closed when enable flag unset)
- [ ] Schema(s) for cycle state / Learning Review with authority flags const false
- [ ] Begin composes C1 freshness/SHA (when available), C3 assessment, capability-plan/task-graph pointers, and Experience similarity hits
- [ ] Checkpoint is idempotent per execution-id + checkpoint key; does not mutate plan approval status or expand scope
- [ ] Close writes/finalizes ExecutionRun + Experience via existing telemetry store contracts; triggers behavior evaluation/pattern draft paths when enabled; never auto-promotes
- [ ] Learning Review packet lists draft proposals with evidence paths only (no install/activate)
- [ ] Hermetic lifecycle fixture covering begin → checkpoint → close → review
- [ ] Doctor + unit tests green; evidence under `.agent/evidence/c4-cognitive-core-adaptive-loop/`
- [ ] Memory docs + CHANGELOG + VERSION **v1.63.0**; ADR-081
- [ ] PR opened (standing order after approval)

## Non-Goals

- C5 Adaptive routing / model switching
- C6 REA deep analysis
- C7 Training bridge / weight export
- Auto-promote or install Skills / activate Policies
- Auto-merge PRs or cut releases
- Live model weight changes
- Expanding autonomy budgets without Captain approval
- HTTP Cognitive Core API surface (remain CLI/orchestrator for this milestone)
- External cognitive-core package extract

## Affected systems

| Area | Change |
|---|---|
| `orchestrator/cycle/` (new) or `orchestrator/cognitive/cycle.py` | State machine + compose services |
| `orchestrator/schemas/` | `cycle-state` / `learning-review` schemas |
| `scripts/` | `run-cycle.sh` + `northstar cycle|learning` wiring |
| Existing | Reuse `assess/`, `cognitive/`, `telemetry/`, `behavior/`, `learning/` — thin adapters, no gate weakening |
| `scripts/doctor.sh` | schema + fail-closed smoke |
| Tests / fixtures | Hermetic cycle lifecycle |
| Project memory | PLAN / PROGRESS / CHANGELOG / DECISIONS / TESTING / VERSION |

## Capability-plan summary

| Task | Profile | Notes |
|---|---|---|
| discovery | `repository-scout` | Map telemetry/behavior/learning join points |
| architecture | `architecture-agent` | Cycle state machine + schema contracts + rollback |
| implementation | `implementation-agent` | Gated CLI + compose adapters |
| validation | `test-engineer` | Hermetic lifecycle + doctor |
| documentation | `documentation-agent` | Memory + evidence + ADR |

Machine artifacts (gitignored): `.agent/plans/c4-cognitive-core-adaptive-loop/`.

## Workstreams (after approval)

1. Schema + cycle state machine (deterministic, hermetic)
2. Begin/checkpoint/close compose adapters
3. Learning Review packet + CLI/launcher
4. Lifecycle fixture + evidence + docs / release bump

## Validation

- Doctor; unit + hermetic lifecycle tests
- Security: no authority expansion; promotion gates unchanged
- Rollback tag before implementation

## Autonomy Budget (proposed)

| Limit | Value |
|---|---|
| Maximum iterations | 10 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 300 |
| Maximum estimated cost (USD) | 0 |
| Stop on scope change | true |

## Rollback

Documented SHA / tag created only after approval, before implementation.

## Definition of Done

Acceptance criteria checked; evidence recorded; PR open; First Mate inspected.

## Prior closeout (C3)

C3 Difficulty and capability fit **COMPLETE** — merged [#207](https://github.com/loganware05/captains-compass-cursor/pull/207) → `main` @ `28ff856` (**v1.62.0**). Plan ID `c3-cognitive-core-difficulty-fit`. Issue #205 closed.
