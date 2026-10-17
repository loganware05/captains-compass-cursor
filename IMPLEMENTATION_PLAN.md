# Implementation Plan — C3 Cognitive Core Difficulty and Capability Fit

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `c3-cognitive-core-difficulty-fit` |
| Issue | [#205](https://github.com/loganware05/captains-compass-cursor/issues/205) |
| Notion | [Cognitive Core — C3](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.61.0** @ `f1ae35d` (C2 merged #204) |
| Branch | *(create after approval)* `cursor/205-c3-difficulty-fit-64df` |
| Rollback | *(create after approval)* `rollback/pre-c3-cognitive-core-difficulty-fit` |
| Release | **v1.62.0** (proposed) |
| Captain | Logan Ware |
| Created | 2026-10-17 |

## Approval record

| Field | Value |
|---|---|
| Approved by | *(pending)* |
| Approval date | *(pending)* |
| Notes | Post-merge continuation after C2 (#204). Implementation must not begin until Captain explicitly approves this plan. |

## Request

Ship Cognitive Core **C3 — Difficulty and capability fit**: an evidence-backed `ProjectDifficultyAssessment` that combines existing capability-plan signals (gaps, Skill coverage, Experiences, task graph, repo/context complexity, validation burden) into a calibrated 0–100 score + confidence, exposed via a gated operator command.

## Problem Statement

Capability planning already surfaces gaps, ranked Skills, and task graphs, but operators lack a single SHA-cited difficulty/capability-fit result to size autonomy budgets, validation depth, and decomposition. Notion Adaptive Intelligence requires this before C4 cycle controller work.

## Desired Outcome

```bash
COMPASS_ASSESS_ENABLED=1 \
./scripts/northstar assess project --objective "…" [--repo PATH]
```

Returns schema-validated JSON with difficulty score, band, confidence, factor breakdown, and citations (snapshot SHA, Skills, Experiences, graph/plan artifacts). Always `approved_for_execution: false` / `authority_mutation: false`. Never bypasses the plan-approval gate.

### Proposed score (Notion)

`difficulty = 0.25 gap_severity + 0.20 skill_uncertainty + 0.15 repository_complexity + 0.15 task_graph_complexity + 0.15 operational_risk + 0.10 validation_burden`

Bands: 0–24 low · 25–49 moderate · 50–74 high · 75–100 very high. Low historical coverage must lower confidence.

## Acceptance Criteria

- [ ] Gated `northstar assess project` (fail-closed when enable flag unset)
- [ ] Schema `project-difficulty-assessment` with authority flags const false
- [ ] Assessment cites snapshot SHA (reuse C1 brain when available), Skills, Experiences, and task-graph/capability-plan evidence
- [ ] Factor breakdown matches Notion weights (documented constants; tunable only via config file, not silent)
- [ ] Hermetic backtest fixture comparing predicted bands vs recorded outcomes for a small set of completed workstreams (M46–M55 / C1–C2 telemetry or fixtures)
- [ ] Doctor + unit tests green; evidence under `.agent/evidence/c3-cognitive-core-difficulty-fit/`
- [ ] Memory docs + CHANGELOG + VERSION **v1.62.0**; ADR-080
- [ ] PR opened (standing order after approval)

## Non-Goals

- C4 Adaptive Development Loop (`cycle begin|checkpoint|close`)
- C5 Adaptive routing / model switching
- C6 REA deep analysis
- C7 Training bridge
- Auto-approve plans or expand autonomy based on difficulty
- Live HTTP/model required for CI
- Changing capability-plan matcher weights

## Affected systems

| Area | Change |
|---|---|
| `orchestrator/` | New `assess/` (or `cognitive/assess.py`) composing resolver + plan artifacts + brain snapshot |
| `orchestrator/schemas/` | `project-difficulty-assessment.schema.json` |
| `scripts/` | `run-assess.sh` + `northstar assess` |
| `scripts/doctor.sh` | schema + fail-closed smoke |
| Tests / fixtures | Hermetic assess + backtest |
| Project memory | PLAN / PROGRESS / CHANGELOG / DECISIONS / TESTING / VERSION |

## Workstreams (after approval)

1. Schema + scoring engine (deterministic, hermetic)
2. CLI / launcher wiring
3. Backtest fixture + evidence
4. Docs / release bump

## Validation

- Doctor; unit tests; backtest report; security (no authority expansion); rollback tag

## Autonomy Budget (proposed)

| Limit | Value |
|---|---|
| Maximum iterations | 8 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 240 |
| Maximum estimated cost (USD) | 0 |
| Stop on scope change | true |

## Rollback

Documented SHA / tag created only after approval, before implementation.

## Definition of Done

Acceptance criteria checked; evidence recorded; PR open; First Mate inspected.

## Prior closeout (C2)

C2 Memory and Retrieval **COMPLETE** — merged [#204](https://github.com/loganware05/captains-compass-cursor/pull/204) → `main` @ `f1ae35d` (**v1.61.0**). Plan ID `c2-cognitive-core-memory-retrieval`. Issue #203 closed.
