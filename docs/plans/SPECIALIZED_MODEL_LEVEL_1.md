> **COMPLETE** (2026-10-21) — Merged [#232](https://github.com/loganware05/captains-compass-cursor/pull/232)
> → `main` @ `d76ebd0` (**v1.70.0**). Plan ID `specialized-model-level-1`.
> Rollback: `rollback/pre-specialized-model-level-1` @ `2507da6`.
> Evidence: `.agent/evidence/specialized-model-level-1/`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Specialized Model Level 1 — On-Device LoRA

Shipped **v1.70.0**: gated prepare/train/evaluate with external trainer or
hermetic `--dry-run`. Weights stay outside the control repo; never auto-promotes.

## Operator surface

```bash
./scripts/run-specialized-model.sh lora prepare|train|evaluate|pipeline \
  --repo-root . --enable-gates --dry-run \
  [--export-path PATH] [--dataset PATH] [--adapter-root PATH]
./scripts/northstar specialized lora pipeline --repo . --enable-gates --dry-run
```

## Next

Specialized Model Level 2 (`specialized-model-level-2`) — **AWAITING APPROVAL**.
