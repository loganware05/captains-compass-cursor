> **APPROVED / IMPLEMENTING** (2026-10-01) — Captain approved; product impl in progress.
> Active root plan: `IMPLEMENTATION_PLAN.md` (Plan ID `m47-behavior-pattern-learning`).

# M47 — Behavior Pattern Learning

Spec source: [Notion — Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (Post-M46 → M47)

Linear: [OVA-59](https://linear.app/ovaltechnologysolutions/issue/OVA-59/m47-behavior-pattern-learning-v1470)

Prerequisite: M46 merged (#184 / v1.46.0).

See root `IMPLEMENTATION_PLAN.md` for the full approval-gated contract.

## One-line summary

Detect recurring patterns from the M46 behavior ledger and emit **proposal-only**
candidate guidance via `northstar learn` — no Policy/Skill/routing activation.

## Baseline

v1.46.0 @ `cb4f463` → release **v1.47.0**

## Operator surface

```bash
COMPASS_BEHAVIOR_LEARN_ENABLED=1 ./scripts/northstar learn scan --repo .
COMPASS_BEHAVIOR_LEARN_ENABLED=1 ./scripts/northstar learn list --repo .
COMPASS_BEHAVIOR_LEARN_ENABLED=1 ./scripts/northstar learn show <pattern-id> --repo .
```

Artifacts: `.agent/evaluations/behavior/patterns/` (+ `candidates/`).
