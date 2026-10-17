> **AWAITING APPROVAL** — Plan ID `c4-cognitive-core-adaptive-loop`.
> Issue: [#208](https://github.com/loganware05/captains-compass-cursor/issues/208).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C4 — Cognitive Core Adaptive Development Loop

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (Adaptive Development Loop)

Prerequisite: C3 shipped (v1.62.0 / #207 @ `28ff856`).

## One-line summary

Gated `northstar cycle begin|checkpoint|close` + `learning review` composing C1–C3, ExecutionRun/Experience, Behavior Loop, and Skill Learning Loop into one idempotent lifecycle that drafts proposals without promoting them.

## Baseline

v1.62.0 @ `28ff856` → proposed release **v1.63.0**

## Operator surface (proposed)

```bash
COMPASS_CYCLE_ENABLED=1 ./scripts/northstar cycle begin --objective "…" --repo .
COMPASS_CYCLE_ENABLED=1 ./scripts/northstar cycle checkpoint --execution-id <id>
COMPASS_CYCLE_ENABLED=1 ./scripts/northstar cycle close --execution-id <id>
COMPASS_CYCLE_ENABLED=1 ./scripts/northstar learning review --repo .
```

## Non-goals

C5–C7; auto-promote Skills/Policies; auto-merge; live model weight changes; authority expansion.
