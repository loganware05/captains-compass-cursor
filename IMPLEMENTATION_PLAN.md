# Implementation Plan — C3 Cognitive Core Difficulty and Capability Fit

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `c3-cognitive-core-difficulty-fit` |
| Issue | [#205](https://github.com/loganware05/captains-compass-cursor/issues/205) |
| Notion | [Cognitive Core — C3](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.61.0** @ `f1ae35d` (C2 merged #204) |
| Branch | `cursor/205-c3-difficulty-fit-64df` |
| Rollback | `rollback/pre-c3-cognitive-core-difficulty-fit` @ `f1ae35d` |
| Release | **v1.62.0** |
| Captain | Logan Ware |
| Created | 2026-10-17 |
| Approved | 2026-10-17 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-17 |
| Notes | Explicit “I approve c3-cognitive-core-difficulty-fit”. Standing order: implement → validate → commit → open PR. |

## Request

Ship Cognitive Core **C3 — Difficulty and capability fit**: an evidence-backed `ProjectDifficultyAssessment` that combines existing capability-plan signals (gaps, Skill coverage, Experiences, task graph, repo/context complexity, validation burden) into a calibrated 0–100 score + confidence, exposed via a gated operator command.

## Desired Outcome

```bash
COMPASS_ASSESS_ENABLED=1 \
./scripts/northstar assess project --objective "…" [--repo PATH]
```

## Acceptance Criteria

- [x] Gated `northstar assess project` (fail-closed when enable flag unset)
- [x] Schema `project-difficulty-assessment` with authority flags const false
- [x] Assessment cites snapshot SHA (reuse C1 brain when available), Skills, Experiences, and task-graph/capability-plan evidence
- [x] Factor breakdown matches Notion weights
- [x] Hermetic backtest fixture comparing predicted bands vs recorded outcomes
- [x] Doctor + unit tests green; evidence under `.agent/evidence/c3-cognitive-core-difficulty-fit/`
- [x] Memory docs + CHANGELOG + VERSION **v1.62.0**; ADR-080
- [ ] PR opened (standing order)

## Non-Goals

C4–C7; auto-approve; live model required for CI; matcher weight mutation.

## Autonomy Budget

| Limit | Value |
|---|---|
| Maximum iterations | 8 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 240 |
| Maximum estimated cost (USD) | 0 |

## Rollback

`rollback/pre-c3-cognitive-core-difficulty-fit` @ `f1ae35d`
