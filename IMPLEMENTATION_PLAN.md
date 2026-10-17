# Implementation Plan — C5 Cognitive Core Adaptive Routing

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `c5-cognitive-core-adaptive-routing` |
| Issue | [#211](https://github.com/loganware05/captains-compass-cursor/issues/211) |
| Notion | [Cognitive Core — C5 Adaptive routing](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.63.0** @ `6906c1d` (C4 merged #210) |
| Branch | *(create after approval)* `cursor/211-c5-adaptive-routing-64df` |
| Rollback | *(create after approval)* `rollback/pre-c5-cognitive-core-adaptive-routing` |
| Release | **v1.64.0** (proposed) |
| Captain | Logan Ware |
| Created | 2026-10-17 |

## Approval record

| Field | Value |
|---|---|
| Approved by | *(pending)* |
| Approval date | *(pending)* |
| Notes | Post-merge continuation after C4 (#210). Implementation must not begin until Captain explicitly approves this plan. |

## Request

Ship Cognitive Core **C5 — Adaptive routing**: a feature-gated model-route recommendation and hermetic evaluate surface that selects among **local / hosted / premium** adapter classes using C3 difficulty, C1/C2 freshness, model-profile catalog, and task budgets. Switching recommendations must preserve project knowledge citations and required approvals. Measure cost per accepted completed task (and related quality proxies), not price-per-token alone. Never auto-bind or auto-spend.

## Problem Statement

NorthStar already has model profiles, agent routing (`skills route-agents`), and DecisionProvider shadow paths, but operators lack a Cognitive Core–owned, SHA-cited **model class** recommendation that composes difficulty + memory freshness + budgets into an auditable route proposal with offline evaluate. Notion Adaptive Intelligence requires this before REA (C6) and training bridge (C7).

## Desired Outcome

```bash
COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model route --objective "…" [--repo PATH]

COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model evaluate [--fixture PATH] [--repo PATH]
```

Returns schema-validated JSON:

- **route** — candidate model class + profile id, rationale, expected budget, citations (snapshot SHA, assessment id when available), fallback chain; always `approved_for_execution: false` / `authority_mutation: false`
- **evaluate** — hermetic report comparing candidates on cost/quality proxies (accepted-task cost, retries, test-pass proxy, human-correction proxy)

Fail-closed without `COMPASS_ROUTE_ENABLED=1`. No live HTTP required for CI.

### Routing policy (Notion-aligned)

| Class | Intended use |
|---|---|
| `local` | Commit summaries, issue triage, simple retrieval-grounded answers |
| `hosted` | Broad planning / multi-file reasoning on open-weight hosted models |
| `premium` | Difficult multi-file / high operational-risk / security-sensitive work |

Inputs (compose, do not reimplement): C3 `assess project` when assess enabled (or cached assessment id from cycle state), C1 snapshot freshness when brain enabled, model-profile catalog, optional cycle difficulty estimate, Experience outcomes for calibration.

## Acceptance Criteria

- [ ] Gated `northstar model route` and `northstar model evaluate` (fail-closed when enable flag unset)
- [ ] Schema(s) for route proposal + evaluate report with authority flags const false
- [ ] Route cites repository/snapshot SHA and (when available) assessment id / difficulty band
- [ ] Recommendation includes model class, profile ref, rationale, expected budget, and ordered fallbacks
- [ ] Evaluate runs hermetically from fixture (no live model/API required in CI)
- [ ] Does not auto-switch Cursor model bindings, auto-spend, or bypass plan approval
- [ ] Composes with existing `orchestrator/model_profiles`, agent_router, DecisionProvider shadows without weakening their gates
- [ ] Doctor + unit tests green; evidence under `.agent/evidence/c5-cognitive-core-adaptive-routing/`
- [ ] Memory docs + CHANGELOG + VERSION **v1.64.0**; ADR-082
- [ ] PR opened (standing order after approval)

## Non-Goals

- C6 REA deep analysis (`rea investigate`)
- C7 Training bridge / weight export
- Auto-binding live IDE/model settings
- Automatic cloud spend or removing budget caps
- Replacing `skills route-agents` wakeability router (may cite it; must not break it)
- HTTP `/v1/route` public API (CLI/orchestrator only this milestone)
- External cognitive-core package extract

## Affected systems

| Area | Change |
|---|---|
| `orchestrator/route/` (new) or `orchestrator/cognitive/route.py` | Route + evaluate services |
| `orchestrator/schemas/` | `model-route-proposal` / `model-route-eval-report` |
| `orchestrator/model_profiles/` | Read-only catalog consume |
| `scripts/` | `run-model-route.sh` + `northstar model` wiring |
| Existing | Optional compose with `assess/`, `cognitive/`, `cycle/`, DecisionProvider shadows |
| `scripts/doctor.sh` | schema + fail-closed smoke |
| Tests / fixtures | Hermetic route + evaluate |
| Project memory | PLAN / PROGRESS / CHANGELOG / DECISIONS / TESTING / VERSION |

## Workstreams (after approval)

1. Schema + deterministic route scorer (class selection from difficulty/freshness/security)
2. Evaluate harness + fixture baselines
3. CLI / launcher + doctor
4. Docs / evidence / release bump

## Validation

- Doctor; unit + hermetic evaluate tests
- Security: no authority expansion; no silent live model switch
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

## Prior closeout (C4)

C4 Adaptive Development Loop **COMPLETE** — merged [#210](https://github.com/loganware05/captains-compass-cursor/pull/210) → `main` @ `6906c1d` (**v1.63.0**). Plan ID `c4-cognitive-core-adaptive-loop`. Issue #208 closed. Prior docs closeout [#209](https://github.com/loganware05/captains-compass-cursor/pull/209) already on main.
