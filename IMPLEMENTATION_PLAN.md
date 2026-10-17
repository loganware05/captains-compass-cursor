# Implementation Plan — C5 Cognitive Core Adaptive Routing

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `c5-cognitive-core-adaptive-routing` |
| Issue | [#211](https://github.com/loganware05/captains-compass-cursor/issues/211) |
| Notion | [Cognitive Core — C5 Adaptive routing](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.63.0** @ `d8f1ac4` (C4 closeout #212 on main) |
| Branch | `cursor/211-c5-adaptive-routing-64df` |
| PR | [#213](https://github.com/loganware05/captains-compass-cursor/pull/213) (draft) |
| Rollback | `rollback/pre-c5-cognitive-core-adaptive-routing` @ `d8f1ac4` |
| Release | **v1.64.0** |
| Captain | Logan Ware |
| Created | 2026-10-17 |
| Approved | 2026-10-17 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-17 |
| Notes | Explicit “I approve c5-cognitive-core-adaptive-routing”; #212 merged. Standing order: implement → validate → commit → open PR. |

## Request

Ship Cognitive Core **C5 — Adaptive routing**: gated `northstar model route|evaluate` selecting local/hosted/premium adapter classes with hermetic cost/quality evaluation. Never auto-switch live models or expand authority.

## Desired Outcome

```bash
COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model route --objective "…" --repo .

COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model evaluate [--fixture PATH] --repo .
```

## Acceptance Criteria

- [x] Gated `northstar model route` and `northstar model evaluate` (fail-closed when enable flag unset)
- [x] Schema(s) for route proposal + evaluate report with authority flags const false
- [x] Route cites repository/snapshot SHA and (when available) assessment id / difficulty band
- [x] Recommendation includes model class, profile ref, rationale, expected budget, and ordered fallbacks
- [x] Evaluate runs hermetically from fixture (no live model/API required in CI)
- [x] Does not auto-switch Cursor model bindings, auto-spend, or bypass plan approval
- [x] Composes with existing `orchestrator/model_profiles`, assess/brain when enabled
- [x] Doctor + unit tests green; evidence under `.agent/evidence/c5-cognitive-core-adaptive-routing/`
- [x] Memory docs + CHANGELOG + VERSION **v1.64.0**; ADR-082
- [x] PR opened (standing order) — [#213](https://github.com/loganware05/captains-compass-cursor/pull/213)

## Non-Goals

C6–C7; auto-bind live models; auto-spend; HTTP `/v1/route` API; external package extract.

## Autonomy Budget

| Limit | Value |
|---|---|
| Maximum iterations | 10 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 300 |
| Maximum estimated cost (USD) | 0 |

## Rollback

`rollback/pre-c5-cognitive-core-adaptive-routing` @ `d8f1ac4`
