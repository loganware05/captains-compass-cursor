# Progress

## Current status

**Specialized Model Level 3 — AWAITING APPROVAL** (docs PR pending) on plan
`specialized-model-level-3`.
Specialized Model Level 2 **COMPLETE** (#234 / **v1.71.0** @ `5727802`).

| Item | Value |
|---|---|
| On main | **v1.71.0** Level 2 (#234) @ `5727802` |
| Active plan | `specialized-model-level-3` **AWAITING APPROVAL** |
| Next | Captain file issue + approve Level 3 → implement → commit → PR |

## Cognitive Core / Specialized Model track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) |
| Read-only persistent oversight | **Complete** (#227 / v1.68.0) |
| Specialized Model Level 0 | **Complete** (#230 / v1.69.0) |
| Specialized Model Level 1 | **Complete** (#232 / v1.70.0) |
| Specialized Model Level 2 | **Complete** (#234 / v1.71.0) |
| Specialized Model Level 3 | **Next** (48–80GB GPU job class) |

## Operator

```bash
./scripts/run-specialized-model.sh gpu pipeline --repo-root . --enable-gates --dry-run \
  --dataset tests/fixtures/specialized-model-gpu/sample-dataset.json
./scripts/northstar specialized gpu pipeline --repo . --enable-gates --dry-run
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Level 2 / #234** — Specialized Model Level 2 rented GPU QLoRA (v1.71.0)
- **Docs PR / #233** — Level 1 COMPLETE + Level 2 plan
- **Level 1 / #232** — Specialized Model Level 1 (v1.70.0)

## Follow-on (after Level 3)

1. Specialized Model Level 4 (multi-GPU cloud) — only if Level 3 shows limits + ROI

## Blockers

None — waiting on Captain approval of `specialized-model-level-3` (and a
tracking GitHub issue).
