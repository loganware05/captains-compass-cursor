# Progress

## Current status

**N1 Operational Reconciliation — AWAITING APPROVAL** on plan
`n1-operational-reconciliation` (proposed **v1.71.1**).
Specialized Model Level 3 (`specialized-model-level-3`) is **DEFERRED** until
N1–N3 consolidation and Level 0–2 proof-of-value.
Specialized Model Level 2 **COMPLETE** (#234 / **v1.71.0**); docs closeout
#235 @ `15e8866`.

| Item | Value |
|---|---|
| On main | **v1.71.0** Level 2 (#234) + docs (#235) @ `15e8866` |
| Active plan | `n1-operational-reconciliation` **AWAITING APPROVAL** |
| Deferred | `specialized-model-level-3` (proposed v1.72.0 when re-approved) |
| Next after N1 | N2 Product Integration Validation → N3 Adaptive Intelligence Validation |

## Cognitive Core / Specialized Model / Consolidation track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) — issue #220 still open (N1 ledger) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) — issue #222 still open (N1 ledger) |
| Read-only persistent oversight | **Complete** (#227 / v1.68.0) |
| Specialized Model Level 0 | **Complete** (#230 / v1.69.0) |
| Specialized Model Level 1 | **Complete** (#232 / v1.70.0) |
| Specialized Model Level 2 | **Complete** (#234 / v1.71.0) |
| **N1** Operational Reconciliation | **Next** (AWAITING APPROVAL) |
| **N2** Product Integration Validation | Follow-on stub |
| **N3** Adaptive Intelligence Validation | Follow-on stub |
| Specialized Model Level 3 | **Deferred** (48–80GB GPU job class) |

## Operator

```bash
# Level 2 harness (unchanged)
./scripts/northstar specialized gpu pipeline --repo . --enable-gates --dry-run

# N1 will extend (if approved): status closeout report
./scripts/northstar status snapshot --repo .
./scripts/northstar oversight run --repo . --enable-gates
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Docs / #235** — Level 2 COMPLETE + Level 3 plan (now superseded as active-next by N1)
- **Level 2 / #234** — Specialized Model Level 2 rented GPU QLoRA (v1.71.0)
- **Docs PR / #233** — Level 1 COMPLETE + Level 2 plan
- **Level 1 / #232** — Specialized Model Level 1 (v1.70.0)

## Follow-on (after N1–N3)

1. Re-approve Specialized Model Level 3 only if Level 0–2 show VRAM/context/ROI limits
2. Specialized Model Level 4 (multi-GPU) — only if Level 3 shows limits + ROI

## Blockers

None — waiting on Captain approval of `n1-operational-reconciliation` (and a
tracking GitHub issue). Agent must not auto-close open issues during N1.
