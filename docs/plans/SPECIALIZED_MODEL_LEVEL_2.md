> **COMPLETE** (2026-10-21) — Merged [#234](https://github.com/loganware05/captains-compass-cursor/pull/234)
> → `main` @ `5727802` (**v1.71.0**). Plan ID `specialized-model-level-2`.
> Rollback: `rollback/pre-specialized-model-level-2` @ `e5256f1`.
> Evidence: `.agent/evidence/specialized-model-level-2/`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Specialized Model Level 2 — Single Rented GPU (QLoRA)

Shipped **v1.71.0**: gated prepare/submit/evaluate with external GPU runner or
hermetic `--dry-run`. Non-dry-run submit requires `--cost-ack`. Weights stay
outside the control repo; never auto-promotes.

## Operator surface

```bash
./scripts/run-specialized-model.sh gpu prepare|submit|evaluate|pipeline \
  --repo-root . --enable-gates --dry-run \
  [--dataset PATH] [--job PATH] [--adapter-root PATH] [--cost-ack]
./scripts/northstar specialized gpu pipeline --repo . --enable-gates --dry-run
```

## Next

Specialized Model Level 3 (`specialized-model-level-3`) — **AWAITING APPROVAL**.
