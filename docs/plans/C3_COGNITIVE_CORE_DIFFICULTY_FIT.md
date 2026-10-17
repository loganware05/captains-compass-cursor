> **APPROVED** (2026-10-17) — Plan ID `c3-cognitive-core-difficulty-fit`.
> Issue: [#205](https://github.com/loganware05/captains-compass-cursor/issues/205).
> Branch: `cursor/205-c3-difficulty-fit-64df` · Rollback `rollback/pre-c3-cognitive-core-difficulty-fit`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C3 — Cognitive Core Difficulty and Capability Fit

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (C3 / Project Difficulty section)

Prerequisite: C2 shipped (v1.61.0 / #204 @ `f1ae35d`).

## One-line summary

Gated `northstar assess project` producing SHA-cited `ProjectDifficultyAssessment` (score + confidence + factor breakdown) without expanding authority.

## Baseline

v1.61.0 @ `f1ae35d` → proposed release **v1.62.0**

## Operator surface

```bash
COMPASS_ASSESS_ENABLED=1 \
./scripts/northstar assess project --objective "…" --repo .
```

## Non-goals

C4–C7; auto-approve; live model required for CI.
