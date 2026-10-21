# Progress

## Current status

**Specialized Model Level 0 — AWAITING APPROVAL** (docs PR pending) on plan
`specialized-model-level-0`
([#228](https://github.com/loganware05/captains-compass-cursor/issues/228)).
Read-only persistent oversight **COMPLETE** (#227 / **v1.68.0** @ `f5bbf24`).

| Item | Value |
|---|---|
| On main | **v1.68.0** oversight (#227) @ `f5bbf24` |
| Active plan | `specialized-model-level-0` **AWAITING APPROVAL** |
| Next | Captain approve Level 0 → implement → commit → PR |

## Cognitive Core / Specialized Model track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) |
| Read-only persistent oversight | **Complete** (#227 / v1.68.0) |
| Specialized Model Level 0 | **Next** (#228) |

## Operator

```bash
./scripts/run-oversight.sh --repo-root . --enable-gates [--since SHA]
./scripts/northstar cognitive e2e --repo . --enable-gates
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Oversight / #227** — read-only persistent oversight (v1.68.0)
- **Docs PR / #226** — E2E COMPLETE + oversight plan
- **E2E / #224** — Cognitive Core C1–C7 hermetic evaluation (v1.67.0)

## Follow-on (after Level 0)

1. Specialized Model Level 1 (on-device LoRA) — only after Level 0 baseline

## Blockers

None — waiting on Captain approval of `specialized-model-level-0`.
