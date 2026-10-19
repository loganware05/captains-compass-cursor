> **APPROVED / IN PROGRESS** — Plan ID `c7-cognitive-core-training-bridge`.
> Issue: [#217](https://github.com/loganware05/captains-compass-cursor/issues/217).
> Branch: `cursor/217-c7-training-bridge-64df`.
> Rollback: `rollback/pre-c7-cognitive-core-training-bridge` @ `f16e8bb`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C7 — Cognitive Core Training Bridge

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (Training bridge)
Cross-page: Specialized Model owns weights/adapters/datasets; Cognitive Core owns export governance.

Prerequisite: C6 shipped (v1.65.0 / #216 @ `1308b5f`); closeout #218 @ `f16e8bb`.

## One-line summary

Gated export of permission-checked, reviewed trajectories into a Specialized Model dataset hand-off package — Captain-gated promotion after independent eval and security; never auto-changes live weights.

## Baseline

v1.65.0 @ `f16e8bb` → release **v1.66.0**

## Operator surface

```bash
COMPASS_TRAIN_BRIDGE_ENABLED=1 \
./scripts/northstar train export \
  --from experiences|cycles \
  --export-authorized --secrets-redacted-ack \
  --license-reviewed --pii-reviewed \
  --specialized-model-handoff-ack \
  [--plan-id ID] [--out PATH] --repo .

COMPASS_TRAIN_BRIDGE_ENABLED=1 \
./scripts/northstar train review --export-id ID --repo .
```

## Non-goals

Auto weight changes; auto-merge; silent cloud upload; replacing Specialized Model ownership of training; bypassing Captain promotion gates.

## Schemas

- `orchestrator/schemas/training-export-manifest.schema.json`
- `orchestrator/schemas/training-export-review.schema.json`

Authority locks: `approved_for_execution`, `authority_mutation`, `auto_uploaded` const `false`.

## Evidence

`.agent/evidence/c7-cognitive-core-training-bridge/`
