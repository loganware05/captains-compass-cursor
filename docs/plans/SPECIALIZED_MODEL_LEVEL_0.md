> **COMPLETE** (2026-10-21) — Merged [#230](https://github.com/loganware05/captains-compass-cursor/pull/230)
> → `main` @ `e04169d` (**v1.69.0**). Plan ID `specialized-model-level-0`.
> Issue: [#228](https://github.com/loganware05/captains-compass-cursor/issues/228) (close when convenient).
> Rollback: `rollback/pre-specialized-model-level-0` @ `6ffa7c7`.
> Evidence: `.agent/evidence/specialized-model-level-0/`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Specialized Model Level 0 — Local Baseline (No Fine-Tuning)

Shipped **v1.69.0**: gated hermetic local baseline over a 24-task held-out gold
set with optional C7 export attach. Weights stay outside the control repo.

## Operator surface

```bash
./scripts/run-specialized-model.sh baseline --repo-root . --enable-gates \
  [--gold PATH] [--export-id ID | --export-path PATH]
./scripts/northstar specialized baseline --repo . --enable-gates
```

## Next

Specialized Model Level 1 (`specialized-model-level-1`) — **AWAITING APPROVAL**.
