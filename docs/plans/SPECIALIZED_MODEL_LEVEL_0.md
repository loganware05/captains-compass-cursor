> **PR OPEN** — Plan ID `specialized-model-level-0`.
> Issue: [#228](https://github.com/loganware05/captains-compass-cursor/issues/228).
> Branch: `cursor/228-specialized-model-level-0-3ec1`.
> Rollback: `rollback/pre-specialized-model-level-0` @ `6ffa7c7`.
> Notion: [Specialized Model](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Specialized Model Level 0 — Local Baseline (No Fine-Tuning)

Shipped toward **v1.69.0**: no-training local baseline over a held-out gold set
with optional C7 export attach. Weights stay outside the control repo.

## Operator surface

```bash
./scripts/run-specialized-model.sh baseline --repo-root . --enable-gates \
  [--gold PATH] [--export-id ID | --export-path PATH]
./scripts/northstar specialized baseline --repo . --enable-gates
```

## Non-goals

LoRA/QLoRA (Level 1+), weight promotion, training HEAD into weights as a
retrieval substitute, automatic uploads, live GPU rental.
