> **APPROVED** (2026-10-19) — Plan ID `c6-cognitive-core-rea-deep-analysis`.
> Issue: [#214](https://github.com/loganware05/captains-compass-cursor/issues/214).
> Branch: `cursor/214-c6-rea-deep-analysis-64df` · Rollback `rollback/pre-c6-cognitive-core-rea-deep-analysis`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C6 — Cognitive Core REA Deep Analysis

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (REA Deep Analysis)
Tooling: [REA](https://github.com/morluto/rea)

Prerequisite: C5 shipped (v1.64.0 / #213) + closeout (#215 @ `735cb6a`).

## One-line summary

Gated `northstar rea investigate` with permission checklist and hermetic fixture default, producing versioned evidence packets that separate observed facts from hypotheses.

## Baseline

v1.64.0 @ `735cb6a` → release **v1.65.0**

## Operator surface

```bash
COMPASS_REA_ENABLED=1 \
./scripts/northstar rea investigate \
  --target PATH_OR_URL --question TEXT [--mode MODE] --repo .
```

Live path: `--allow-live` + complete checklist flags; auto-execution withheld (detect-only stub when REA binary present).

## Non-goals

C7; automatic REA; speculative training-data recovery; HTTP REA API; authority expansion.
