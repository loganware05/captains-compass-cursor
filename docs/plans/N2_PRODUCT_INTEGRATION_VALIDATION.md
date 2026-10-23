> **COMPLETE** (2026-10-22) — Plan ID `n2-product-integration-validation`.
> Baseline: **v1.71.1** @ `e0d813d` / [#238](https://github.com/loganware05/captains-compass-cursor/pull/238).
> Release: **v1.72.0**.
> Target: `captain-compass-sandbox` (Compass **1.71.1**).
> Evidence: `.agent/evidence/n2-product-integration-validation/`.
> Rollback: `rollback/pre-n2-product-integration-validation` @ `e0d813d`.

# N2 — Product Integration Validation

## One-line summary

Refreshed sandbox to current control VERSION, exercised the full NorthStar
lifecycle with evidence, shipped a bounded product feature, and fixed
product-repo `assess` via `COMPASS_CONTROL_ROOT` profile fallback.

## Operator note

```bash
export COMPASS_CONTROL_ROOT=/path/to/captains-compass-cursor   # set by northstar
COMPASS_ASSESS_ENABLED=1 ./scripts/northstar assess project \
  --objective "…" --repo /path/to/product
```

## Follow-on

**N3** Adaptive Intelligence Validation **COMPLETE** (**v1.73.0**).
Level 3 remains **DEFERRED**.
