# Implementation Plan — C4 Cognitive Core Adaptive Development Loop

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `c4-cognitive-core-adaptive-loop` |
| Issue | [#208](https://github.com/loganware05/captains-compass-cursor/issues/208) |
| Notion | [Cognitive Core — C4 Adaptive Development Loop](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.62.0** @ `9f78bda` (C3 closeout #209 on main) |
| Branch | `cursor/208-c4-adaptive-loop-64df` |
| Rollback | `rollback/pre-c4-cognitive-core-adaptive-loop` @ `9f78bda` |
| Release | **v1.63.0** |
| Captain | Logan Ware |
| Created | 2026-10-17 |
| Approved | 2026-10-17 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-17 |
| Notes | Explicit “I approve c4-cognitive-core-adaptive-loop”. Standing order: implement → validate → commit → open PR. |

## Request

Ship Cognitive Core **C4 — Adaptive Development Loop**: an idempotent, feature-gated controller that connects existing planning, C1–C3 Cognitive Core surfaces, ExecutionRun/Experience telemetry, Behavior Loop evaluation/pattern scan, and Skill Learning Loop draft paths into one lifecycle (`cycle begin|checkpoint|close` + `learning review`). Automate evidence capture and proposal generation only — never promotion, merge, or authority expansion.

## Desired Outcome

```bash
COMPASS_CYCLE_ENABLED=1 COMPASS_ASSESS_ENABLED=1 \
./scripts/northstar cycle begin --objective "…" --repo .

COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar cycle checkpoint --execution-id <id> --checkpoint-key <key>

COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar cycle close --execution-id <id>

COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar learning review --repo .
```

## Acceptance Criteria

- [x] Gated `northstar cycle begin|checkpoint|close` and `learning review` (fail-closed when enable flag unset)
- [x] Schema(s) for cycle state / Learning Review with authority flags const false
- [x] Begin composes C1 freshness/SHA (when available), C3 assessment, capability-plan/task-graph pointers, and Experience similarity hits
- [x] Checkpoint is idempotent per execution-id + checkpoint key; does not mutate plan approval status or expand scope
- [x] Close writes/finalizes ExecutionRun + Experience via existing telemetry store contracts; optional behavior eval when enabled; never auto-promotes
- [x] Learning Review packet lists draft proposals with evidence paths only (no install/activate)
- [x] Hermetic lifecycle fixture covering begin → checkpoint → close → review
- [x] Doctor + unit tests green; evidence under `.agent/evidence/c4-cognitive-core-adaptive-loop/`
- [x] Memory docs + CHANGELOG + VERSION **v1.63.0**; ADR-081
- [ ] PR opened (standing order)

## Non-Goals

C5–C7; auto-promote; auto-merge; live model weight changes; HTTP Cognitive Core API; external package extract.

## Autonomy Budget

| Limit | Value |
|---|---|
| Maximum iterations | 10 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 300 |
| Maximum estimated cost (USD) | 0 |

## Rollback

`rollback/pre-c4-cognitive-core-adaptive-loop` @ `9f78bda`
