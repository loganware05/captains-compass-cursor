> **COMPLETE** (2026-10-01) — Merged [#185](https://github.com/loganware05/captains-compass-cursor/pull/185) → `main` @ `402573e` (v1.47.0).

# M47 — Behavior Pattern Learning

Spec source: [Notion — Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (Post-M46 → M47)

Linear: [OVA-59](https://linear.app/ovaltechnologysolutions/issue/OVA-59/m47-behavior-pattern-learning-v1470) **Done**

## One-line summary

Detect recurring patterns from the M46 behavior ledger and emit **proposal-only**
candidate guidance via `northstar learn` — no Policy/Skill/routing activation.

## Shipped

- Release **v1.47.0**
- `COMPASS_BEHAVIOR_LEARN_ENABLED` + `northstar learn`
- Grouping: signal + agent + skill + polarity; `min_occurrence` default 3
- Artifacts: `.agent/evaluations/behavior/patterns/` (+ `candidates/`)
- ADR-064; evidence `.agent/evidence/m47-behavior-pattern-learning/`

## Operator surface

```bash
COMPASS_BEHAVIOR_LEARN_ENABLED=1 ./scripts/northstar learn scan --repo .
COMPASS_BEHAVIOR_LEARN_ENABLED=1 ./scripts/northstar learn list --repo .
COMPASS_BEHAVIOR_LEARN_ENABLED=1 ./scripts/northstar learn show <pattern-id> --repo .
```
