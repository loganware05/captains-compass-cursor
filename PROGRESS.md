# Progress

## Current status

**Specialized Model Level 2 — PR OPEN**
([#234](https://github.com/loganware05/captains-compass-cursor/pull/234))
on plan `specialized-model-level-2`.
Implementation toward **v1.71.0** on branch
`cursor/specialized-model-level-2-3ec1`. Rollback
`rollback/pre-specialized-model-level-2` @ `e5256f1`.

| Item | Value |
|---|---|
| On main | **v1.70.0** Level 1 (#232) + docs (#233) @ `e5256f1` |
| Active plan | `specialized-model-level-2` **APPROVED** / implementing |
| Next | Merge Level 2 PR → Captain closeout |

## Cognitive Core / Specialized Model track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) |
| Read-only persistent oversight | **Complete** (#227 / v1.68.0) |
| Specialized Model Level 0 | **Complete** (#230 / v1.69.0) |
| Specialized Model Level 1 | **Complete** (#232 / v1.70.0) |
| Specialized Model Level 2 | **In PR** → v1.71.0 |

## Operator

```bash
./scripts/run-specialized-model.sh gpu pipeline --repo-root . --enable-gates \
  --dataset tests/fixtures/specialized-model-gpu/sample-dataset.json --dry-run
./scripts/northstar specialized gpu pipeline --repo . --enable-gates --dry-run
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Docs PR / #233** — Level 1 COMPLETE + Level 2 plan
- **Level 1 / #232** — Specialized Model Level 1 (v1.70.0)
- **Level 0 / #230** — Specialized Model Level 0 (v1.69.0)

## Follow-on (after Level 2)

1. Specialized Model Level 3 (48–80GB GPU) — only if Level 2 shows limits + ROI

## Blockers

None — awaiting Captain merge of Level 2 PR.
