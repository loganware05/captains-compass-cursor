> **PR OPEN** — [#232](https://github.com/loganware05/captains-compass-cursor/pull/232).
> Plan ID `specialized-model-level-1`.
> Docs PR: [#231](https://github.com/loganware05/captains-compass-cursor/pull/231).
> Branch: `cursor/specialized-model-level-1-3ec1`.
> Rollback: `rollback/pre-specialized-model-level-1` @ `2507da6`.
> Notion: [Specialized Model](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Specialized Model Level 1 — On-Device LoRA

Shipped toward **v1.70.0**: gated prepare/train/evaluate with external trainer
or hermetic `--dry-run`. Weights stay outside the control repo; never
auto-promotes.

## Operator surface

```bash
./scripts/run-specialized-model.sh lora prepare|train|evaluate|pipeline \
  --repo-root . --enable-gates --dry-run \
  [--export-path PATH] [--dataset PATH] [--adapter-root PATH]
./scripts/northstar specialized lora pipeline --repo . --enable-gates --dry-run
```

Live train: set `COMPASS_SPECIALIZED_LORA_TRAINER` and
`COMPASS_SPECIALIZED_ADAPTER_ROOT` (outside this repo).

## Non-goals

Level 2+ rented GPU; storing weights in this repo; auto-promotion into Adaptive
Intelligence routing.
