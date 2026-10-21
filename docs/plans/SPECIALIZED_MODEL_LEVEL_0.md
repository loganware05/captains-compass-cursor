> **AWAITING APPROVAL** (2026-10-21) — Plan ID `specialized-model-level-0`.
> Issue: [#228](https://github.com/loganware05/captains-compass-cursor/issues/228).
> Notion: [Specialized Model](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Specialized Model Level 0 — Local Baseline (No Fine-Tuning)

Prerequisite: C7 training bridge + E2E + oversight shipped through **v1.68.0**.

## One-line summary

No-training local baseline: freeze a held-out gold set, score retrieval/prompt
(and optional local student stub) against C7 reviewed exports — weights stay
outside the control repo; no LoRA.

## Proposed operator surface

```bash
COMPASS_SPECIALIZED_MODEL_ENABLED=1 \
  ./scripts/northstar specialized baseline --repo . [--export-id ID] [--gold PATH]
```

## Non-goals

LoRA/QLoRA (Level 1+), weight promotion, training HEAD into weights as a
retrieval substitute, automatic uploads, live GPU rental.
