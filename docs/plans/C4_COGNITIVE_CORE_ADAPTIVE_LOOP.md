> **APPROVED** (2026-10-17) — Plan ID `c4-cognitive-core-adaptive-loop`.
> Issue: [#208](https://github.com/loganware05/captains-compass-cursor/issues/208).
> Branch: `cursor/208-c4-adaptive-loop-64df` · Rollback `rollback/pre-c4-cognitive-core-adaptive-loop`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C4 — Cognitive Core Adaptive Development Loop

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (Adaptive Development Loop)

Prerequisite: C3 shipped (v1.62.0 / #207) + closeout (#209 @ `9f78bda`).

## One-line summary

Gated `northstar cycle begin|checkpoint|close` + `learning review` composing C1–C3, ExecutionRun/Experience, Behavior Loop, and Skill Learning Loop into one idempotent lifecycle that drafts proposals without promoting them.

## Baseline

v1.62.0 @ `9f78bda` → release **v1.63.0**

## Operator surface

```bash
COMPASS_CYCLE_ENABLED=1 COMPASS_ASSESS_ENABLED=1 \
./scripts/northstar cycle begin --objective "…" --repo .
COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar cycle checkpoint --execution-id <id> --checkpoint-key <key> --repo .
COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar cycle close --execution-id <id> --repo .
COMPASS_CYCLE_ENABLED=1 \
./scripts/northstar learning review --repo .
```

## Non-goals

C5–C7; auto-promote Skills/Policies; auto-merge; live model weight changes; authority expansion.
