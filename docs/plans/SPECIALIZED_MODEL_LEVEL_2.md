> **AWAITING APPROVAL** (2026-10-21) — Plan ID `specialized-model-level-2`.
> Prerequisite: Level 1 **v1.70.0** / [#232](https://github.com/loganware05/captains-compass-cursor/pull/232).
> Notion: [Specialized Model](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.
> Issue: Captain files GitHub issue before or on approval (agent cannot create issues).

# Specialized Model Level 2 — Single Rented GPU (QLoRA)

Prerequisite: Level 1 on-device LoRA harness shipped (**v1.70.0**).

## One-line summary

Captain-cost-gated single rented GPU (≈16–24GB VRAM) QLoRA path for 3B–8B
students: job manifest + remote trainer contract, cost estimate/ack, eval vs
Level 0/1 baselines on the held-out gold set — weights outside the control
repo; never auto-promote into Adaptive Intelligence.

## Proposed operator surface

```bash
COMPASS_SPECIALIZED_MODEL_ENABLED=1 \
  ./scripts/northstar specialized gpu prepare|submit|evaluate \
    --repo . [--dataset PATH] [--cost-ack] [--dry-run]
```

`submit` invokes an **external** GPU job runner (env/path); control repo
records manifests + cost + eval only. CI stays hermetic (`--dry-run`).

## Non-goals

Level 3+ multi-GPU / research cluster; storing weights in this repo;
automatic promotion; spending without Captain cost ack; live GPU jobs in CI.
