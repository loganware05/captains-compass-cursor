# Progress

## Current status

**Specialized Model Level 1 — AWAITING APPROVAL** (docs PR pending) on plan
`specialized-model-level-1`.
Specialized Model Level 0 **COMPLETE** (#230 / **v1.69.0** @ `e04169d`).

| Item | Value |
|---|---|
| On main | **v1.69.0** Level 0 (#230) @ `e04169d` |
| Active plan | `specialized-model-level-1` **AWAITING APPROVAL** |
| Next | Captain file issue + approve Level 1 → implement → commit → PR |

## Cognitive Core / Specialized Model track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) |
| Read-only persistent oversight | **Complete** (#227 / v1.68.0) |
| Specialized Model Level 0 | **Complete** (#230 / v1.69.0) |
| Specialized Model Level 1 | **Next** (on-device LoRA) |

## Operator

```bash
./scripts/run-specialized-model.sh baseline --repo-root . --enable-gates
./scripts/northstar specialized baseline --repo . --enable-gates
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Level 0 / #230** — Specialized Model Level 0 local baseline (v1.69.0)
- **Docs PR / #229** — oversight COMPLETE + Level 0 plan
- **Oversight / #227** — read-only persistent oversight (v1.68.0)

## Follow-on (after Level 1)

1. Specialized Model Level 2 (single rented GPU) — only if Level 1 shows limits + ROI

## Blockers

None — waiting on Captain approval of `specialized-model-level-1` (and a
tracking GitHub issue).
