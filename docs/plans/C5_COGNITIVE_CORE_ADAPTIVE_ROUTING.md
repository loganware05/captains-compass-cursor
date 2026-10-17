> **APPROVED** (2026-10-17) — Plan ID `c5-cognitive-core-adaptive-routing`.
> Issue: [#211](https://github.com/loganware05/captains-compass-cursor/issues/211).
> Branch: `cursor/211-c5-adaptive-routing-64df` · Rollback `rollback/pre-c5-cognitive-core-adaptive-routing`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C5 — Cognitive Core Adaptive Routing

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (Adaptive routing)

Prerequisite: C4 shipped (v1.63.0 / #210) + closeout (#212 @ `d8f1ac4`).

## One-line summary

Gated `northstar model route|evaluate` recommending local / hosted / premium adapter classes (mapped to model-profile catalog) with hermetic cost/quality ranking — never auto-switches live models.

## Baseline

v1.63.0 @ `d8f1ac4` → release **v1.64.0**

## Operator surface

```bash
COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model route --objective "…" --repo .
COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model evaluate [--fixture PATH] --repo .
```

## Non-goals

C6–C7; auto-bind live models; auto-spend; HTTP route API; REA; training export.
