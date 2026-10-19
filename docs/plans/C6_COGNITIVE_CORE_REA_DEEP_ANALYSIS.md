> **AWAITING APPROVAL** — Plan ID `c6-cognitive-core-rea-deep-analysis`.
> Issue: [#214](https://github.com/loganware05/captains-compass-cursor/issues/214).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C6 — Cognitive Core REA Deep Analysis

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (REA Deep Analysis)
Tooling: [REA](https://github.com/morluto/rea)

Prerequisite: C5 shipped (v1.64.0 / #213 @ `56ac9de`).

## One-line summary

Gated, permission-checked REA investigate surface that produces a versioned evidence packet for one authorized packaged/runtime case — reproducible observation only; never presents speculation as fact.

## Baseline

v1.64.0 @ `56ac9de` → proposed release **v1.65.0**

## Operator surface (proposed)

```bash
COMPASS_REA_ENABLED=1 \
./scripts/northstar rea investigate \
  --target PATH_OR_URL --question TEXT [--mode MODE] --repo .
```

## Non-goals

C7 Training bridge; automatic REA on every task; speculative “recovered training data” claims; authority expansion; live REA required for CI.
