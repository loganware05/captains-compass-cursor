> **AWAITING APPROVAL** (2026-10-20) — Plan ID `e2e-cognitive-core-evaluation`.
> Issue: [#222](https://github.com/loganware05/captains-compass-cursor/issues/222).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# E2E Cognitive Core Evaluation (C1–C7)

Prerequisite: C1–C7 shipped (v1.66.0 / #219) + post-C7 closeout (v1.66.1 / #221).

## One-line summary

Hermetic (then optional sandbox) end-to-end exercise of gated Cognitive Core
surfaces with measured baselines — no new authority.

## Proposed operator surface

```bash
# Control-repo hermetic harness (proposed)
./scripts/run-cognitive-core-e2e.sh --repo . --mode hermetic

# Optional sandbox path after Compass update
./scripts/run-cognitive-core-e2e.sh --repo /path/to/captain-compass-sandbox --mode sandbox
```

## Non-goals

Persistent oversight automation; Specialized Model fine-tuning / weight
promotion; HTTP `/v1/*` server; live REA or live embeddings required for CI.
