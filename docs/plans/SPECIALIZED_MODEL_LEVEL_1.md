> **AWAITING APPROVAL** (2026-10-21) — Plan ID `specialized-model-level-1`.
> Docs PR: [#231](https://github.com/loganware05/captains-compass-cursor/pull/231).
> Prerequisite: Level 0 **v1.69.0** / [#230](https://github.com/loganware05/captains-compass-cursor/pull/230).
> Notion: [Specialized Model](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.
> Issue: Captain files GitHub issue before or on approval (agent cannot create issues).

# Specialized Model Level 1 — On-Device LoRA

Prerequisite: Level 0 baseline shipped (**v1.69.0**).

## One-line summary

Captain-gated on-device LoRA experiment path: build a permission-checked
dataset from C7 reviewed exports, train a small adapter **outside** the control
repo (MLX/MLX-LM on Mac), evaluate adapter vs Level 0 baseline on the held-out
gold set, and record a go/no-go run manifest — never auto-promote weights into
Adaptive Intelligence routing.

## Proposed operator surface

```bash
COMPASS_SPECIALIZED_MODEL_ENABLED=1 \
  ./scripts/northstar specialized lora prepare|train|evaluate \
    --repo . [--export-id ID] [--dataset PATH] [--adapter-root PATH]
```

`train` invokes an **external** trainer (path/env); control repo records
manifests + eval only. CI stays hermetic (fixture adapter / dry-run).

## Non-goals

Level 2+ rented GPU / multi-GPU; storing weights or adapters in this repo;
automatic promotion into live routing; training HEAD into weights as a
retrieval substitute; unreviewed self-training.
