# Progress

## Current status

**Specialized Model Level 0 — PR OPEN**
([#230](https://github.com/loganware05/captains-compass-cursor/pull/230))
on plan `specialized-model-level-0`
([#228](https://github.com/loganware05/captains-compass-cursor/issues/228)).
Implementation toward **v1.69.0** on branch
`cursor/228-specialized-model-level-0-3ec1`. Rollback
`rollback/pre-specialized-model-level-0` @ `6ffa7c7`.

| Item | Value |
|---|---|
| On main | **v1.68.0** oversight (#227) + docs (#229) @ `6ffa7c7` |
| Active plan | `specialized-model-level-0` **APPROVED** / implementing |
| Next | Merge Level 0 PR → Captain closeout |

## Cognitive Core / Specialized Model track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) |
| Read-only persistent oversight | **Complete** (#227 / v1.68.0) |
| Specialized Model Level 0 | **In PR** (#228) → v1.69.0 |

## Operator

```bash
./scripts/run-specialized-model.sh baseline --repo-root . --enable-gates \
  [--export-path tests/fixtures/specialized-model-gold/sample-export.json]
./scripts/northstar specialized baseline --repo . --enable-gates
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Docs PR / #229** — oversight COMPLETE + Level 0 plan
- **Oversight / #227** — read-only persistent oversight (v1.68.0)
- **E2E / #224** — Cognitive Core C1–C7 hermetic evaluation (v1.67.0)

## Follow-on (after Level 0)

1. Specialized Model Level 1 (on-device LoRA) — only after Level 0 baseline

## Blockers

None — awaiting Captain merge of Level 0 PR.
