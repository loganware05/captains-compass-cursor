> **PR OPEN** — [#234](https://github.com/loganware05/captains-compass-cursor/pull/234).
> Plan ID `specialized-model-level-2`.
> Docs PR: [#233](https://github.com/loganware05/captains-compass-cursor/pull/233).
> Branch: `cursor/specialized-model-level-2-3ec1`.
> Rollback: `rollback/pre-specialized-model-level-2` @ `e5256f1`.
> Notion: [Specialized Model](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Specialized Model Level 2 — Single Rented GPU (QLoRA)

Shipped toward **v1.71.0**: gated prepare/submit/evaluate with external GPU
runner or hermetic `--dry-run`. Non-dry-run submit requires `--cost-ack`.
Weights stay outside the control repo; never auto-promotes.

## Operator surface

```bash
./scripts/run-specialized-model.sh gpu prepare|submit|evaluate|pipeline \
  --repo-root . --enable-gates --dry-run \
  [--dataset PATH] [--job PATH] [--adapter-root PATH] [--cost-ack]
./scripts/northstar specialized gpu pipeline --repo . --enable-gates --dry-run
```

Live submit: `--cost-ack` + `COMPASS_SPECIALIZED_GPU_RUNNER` +
`COMPASS_SPECIALIZED_ADAPTER_ROOT` (outside this repo).

## Non-goals

Level 3+ multi-GPU; storing weights in this repo; auto-promotion; unbounded
GPU spend without cost ack.
