> **AWAITING APPROVAL** — Plan ID `c5-cognitive-core-adaptive-routing`.
> Issue: [#211](https://github.com/loganware05/captains-compass-cursor/issues/211).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C5 — Cognitive Core Adaptive Routing

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (Adaptive routing)

Prerequisite: C4 shipped (v1.63.0 / #210 @ `6906c1d`).

## One-line summary

Gated model-route recommendations across local / hosted / premium adapters that preserve project knowledge and approval gates, with hermetic cost/quality evaluation — never silent live model switching.

## Baseline

v1.63.0 @ `6906c1d` → proposed release **v1.64.0**

## Operator surface (proposed)

```bash
COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model route --objective "…" --repo .

COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model evaluate [--fixture PATH] --repo .
```

## Non-goals

C6–C7; auto-switch live Cursor/model bindings; auto-spend without budgets; REA investigate; training export.
