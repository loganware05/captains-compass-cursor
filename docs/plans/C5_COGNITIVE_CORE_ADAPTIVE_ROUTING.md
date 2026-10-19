> **COMPLETE** (2026-10-19) — Merged [#213](https://github.com/loganware05/captains-compass-cursor/pull/213)
> → `main` @ `56ac9de` (**v1.64.0**). Plan ID `c5-cognitive-core-adaptive-routing`.
> Issue: [#211](https://github.com/loganware05/captains-compass-cursor/issues/211) (closed).
> Rollback: `rollback/pre-c5-cognitive-core-adaptive-routing` @ `d8f1ac4`.
> Evidence: `.agent/evidence/c5-cognitive-core-adaptive-routing/`.

# C5 — Cognitive Core Adaptive Routing

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (Adaptive routing)

Prerequisite: C4 shipped (v1.63.0 / #210) + closeout (#212).

## One-line summary

Gated `northstar model route|evaluate` recommending local / hosted / premium adapter classes (mapped to model-profile catalog) with hermetic cost/quality ranking — never auto-switches live models.

## Shipped operator surface

```bash
COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model route --objective "…" --repo .
COMPASS_ROUTE_ENABLED=1 \
./scripts/northstar model evaluate [--fixture PATH] --repo .
```

## Non-goals (honored)

C6–C7; auto-bind live models; auto-spend; HTTP route API; REA; training export.
