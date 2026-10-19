> **AWAITING APPROVAL** — Plan ID `c7-cognitive-core-training-bridge`.
> Issue: [#217](https://github.com/loganware05/captains-compass-cursor/issues/217).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C7 — Cognitive Core Training Bridge

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (Training bridge)
Cross-page: Specialized Model owns weights/adapters/datasets; Cognitive Core owns export governance.

Prerequisite: C6 shipped (v1.65.0 / #216 @ `1308b5f`).

## One-line summary

Gated export of permission-checked, reviewed trajectories into a Specialized Model dataset hand-off package — Captain-gated promotion after independent eval and security; never auto-changes live weights.

## Baseline

v1.65.0 @ `1308b5f` → proposed release **v1.66.0**

## Operator surface (proposed)

```bash
COMPASS_TRAIN_BRIDGE_ENABLED=1 \
./scripts/northstar train export --from experiences|cycles [--out PATH] --repo .

COMPASS_TRAIN_BRIDGE_ENABLED=1 \
./scripts/northstar train review --export-id ID --repo .
```

## Non-goals

Auto weight changes; auto-merge; silent cloud upload; replacing Specialized Model ownership of training; bypassing Captain promotion gates.
