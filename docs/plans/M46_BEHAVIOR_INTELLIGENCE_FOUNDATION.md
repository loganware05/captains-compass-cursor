> **APPROVED** (2026-10-01) — Captain must approve before product implementation.
> Active root plan: `IMPLEMENTATION_PLAN.md` (Plan ID `m46-behavior-intelligence-foundation`).

# M46 — Behavior Intelligence Foundation

Spec source: [Notion — NorthStar Behavioral Intelligence Loop — Sprint Development Plan](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107)

Notion plan mirror: [M46 Implementation Plan](https://app.notion.com/p/3ece6a901c4381a0826dcc5e553daa40)

Linear: [OVA-58](https://linear.app/ovaltechnologysolutions/issue/OVA-58/m46-behavior-intelligence-foundation-v1460) · Project [NorthStar Behavioral Intelligence Loop](https://linear.app/ovaltechnologysolutions/project/northstar-behavioral-intelligence-loop-e24174b3f1ef)

See root `IMPLEMENTATION_PLAN.md` for the full approval-gated contract (scope,
live-repo integration points, workstreams, acceptance criteria, rollback).

## One-line summary

Observe-only behavior evaluation via DecisionProvider + dual ledger +
`northstar evaluate` gated by `COMPASS_BEHAVIOR_EVAL_ENABLED` — no
prompt/Skill/routing/authority mutation.

## Baseline

v1.45.0 @ `0d125c7` → release **v1.46.0** (confirmed)

## Captain-resolved (2026-10-01)

1. Enable flag **and** CLI
2. Both ledger formats (JSON + JSONL)
3. Linear issue + M46–M51 milestones created
4. v1.46.0 confirmed
5. `weak_verification` / `weak_test_coverage` / `unverified_claim` distinct
