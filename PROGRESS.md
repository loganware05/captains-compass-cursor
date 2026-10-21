# Progress

## Current status

**Specialized Model Level 2 — AWAITING APPROVAL** (docs PR pending) on plan
`specialized-model-level-2`.
Specialized Model Level 1 **COMPLETE** (#232 / **v1.70.0** @ `d76ebd0`).

| Item | Value |
|---|---|
| On main | **v1.70.0** Level 1 (#232) @ `d76ebd0` |
| Active plan | `specialized-model-level-2` **AWAITING APPROVAL** |
| Next | Captain file issue + approve Level 2 → implement → commit → PR |

## Cognitive Core / Specialized Model track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) |
| Read-only persistent oversight | **Complete** (#227 / v1.68.0) |
| Specialized Model Level 0 | **Complete** (#230 / v1.69.0) |
| Specialized Model Level 1 | **Complete** (#232 / v1.70.0) |
| Specialized Model Level 2 | **Next** (single rented GPU QLoRA) |

## Operator

```bash
./scripts/run-specialized-model.sh lora pipeline --repo-root . --enable-gates --dry-run \
  --export-path tests/fixtures/specialized-model-gold/sample-export.json
./scripts/northstar specialized lora pipeline --repo . --enable-gates --dry-run
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Level 1 / #232** — Specialized Model Level 1 on-device LoRA (v1.70.0)
- **Docs PR / #231** — Level 0 COMPLETE + Level 1 plan
- **Level 0 / #230** — Specialized Model Level 0 (v1.69.0)

## Follow-on (after Level 2)

1. Specialized Model Level 3 (48–80GB GPU) — only if Level 2 shows limits + ROI

## Blockers

None — waiting on Captain approval of `specialized-model-level-2` (and a
tracking GitHub issue).
