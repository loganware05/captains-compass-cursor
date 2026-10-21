# Progress

## Current status

**Specialized Model Level 1 — PR OPEN**
([#232](https://github.com/loganware05/captains-compass-cursor/pull/232))
on plan `specialized-model-level-1`.
Implementation toward **v1.70.0** on branch
`cursor/specialized-model-level-1-3ec1`. Rollback
`rollback/pre-specialized-model-level-1` @ `2507da6`.

| Item | Value |
|---|---|
| On main | **v1.69.0** Level 0 (#230) + docs (#231) @ `2507da6` |
| Active plan | `specialized-model-level-1` **APPROVED** / implementing |
| Next | Merge Level 1 PR → Captain closeout |

## Cognitive Core / Specialized Model track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) |
| Read-only persistent oversight | **Complete** (#227 / v1.68.0) |
| Specialized Model Level 0 | **Complete** (#230 / v1.69.0) |
| Specialized Model Level 1 | **In PR** → v1.70.0 |

## Operator

```bash
./scripts/run-specialized-model.sh lora pipeline --repo-root . --enable-gates \
  --export-path tests/fixtures/specialized-model-gold/sample-export.json --dry-run
./scripts/northstar specialized lora pipeline --repo . --enable-gates --dry-run
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Docs PR / #231** — Level 0 COMPLETE + Level 1 plan
- **Level 0 / #230** — Specialized Model Level 0 (v1.69.0)
- **Oversight / #227** — read-only persistent oversight (v1.68.0)

## Follow-on (after Level 1)

1. Specialized Model Level 2 (single rented GPU) — only if Level 1 shows limits + ROI

## Blockers

None — awaiting Captain merge of Level 1 PR.
