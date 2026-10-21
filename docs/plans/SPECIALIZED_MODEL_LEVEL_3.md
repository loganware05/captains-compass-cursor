> **AWAITING APPROVAL** (2026-10-21) — Plan ID `specialized-model-level-3`.
> Prerequisite: Level 2 **v1.71.0** / [#234](https://github.com/loganware05/captains-compass-cursor/pull/234).
> Notion: [Specialized Model](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.
> Issue: Captain files GitHub issue before or on approval (agent cannot create issues).

# Specialized Model Level 3 — Large Single GPU (48–80GB)

Prerequisite: Level 2 single rented GPU harness shipped (**v1.71.0**).

## One-line summary

Captain-cost-gated larger single-GPU path (≈48–80GB VRAM) for 7B–14B adapters
with longer context: job class profiles, cost-ack, external runner contract,
eval vs Level 0–2 baselines — weights outside the control repo; never
auto-promote into Adaptive Intelligence.

## Proposed operator surface

```bash
COMPASS_SPECIALIZED_MODEL_ENABLED=1 \
  ./scripts/northstar specialized gpu prepare|submit|evaluate \
    --repo . --class large [--dataset PATH] [--cost-ack] [--dry-run]
```

Reuses Level 2 `gpu` surface with a **job class** (`standard` 16–24GB vs
`large` 48–80GB). CI stays hermetic (`--dry-run`).

## Non-goals

Level 4+ multi-GPU / research cluster; storing weights in this repo;
automatic promotion; spending without Captain cost ack; live GPU jobs in CI.
