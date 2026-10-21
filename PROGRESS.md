# Progress

## Current status

**Read-only persistent oversight — PR OPEN** ([#227](https://github.com/loganware05/captains-compass-cursor/pull/227)) on plan
`read-only-persistent-oversight`
([#225](https://github.com/loganware05/captains-compass-cursor/issues/225)).
Approved 2026-10-21 after #226 merged (**v1.67.0** @ `c5d435e`).

| Item | Value |
|---|---|
| On main | **v1.67.0** (#226) @ `c5d435e` |
| Active plan | `read-only-persistent-oversight` **PR OPEN** ([#227](https://github.com/loganware05/captains-compass-cursor/pull/227)) |
| Branch | `cursor/225-read-only-persistent-oversight-3ec1` |
| Rollback | `rollback/pre-read-only-persistent-oversight` @ `c5d435e` |
| Release | **v1.68.0** |
| Next | Captain merge #227 |

## Cognitive Core track

| Milestone | Status |
|---|---|
| C1–C7 | **Complete** through v1.66.0 |
| Post-C7 closeout | **Complete** (#221 / v1.66.1) |
| E2E Cognitive Core evaluation | **Complete** (#224 / v1.67.0) |
| Read-only persistent oversight | **PR open** ([#227](https://github.com/loganware05/captains-compass-cursor/pull/227) / v1.68.0) |

## Operator

```bash
./scripts/run-oversight.sh --repo-root . --enable-gates [--since SHA]
./scripts/northstar oversight run --repo . --enable-gates
./scripts/northstar status post-merge --repo . --enable-gates
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **Docs PR / #226** — E2E COMPLETE + oversight plan
- **E2E / #224** — Cognitive Core C1–C7 hermetic evaluation (v1.67.0)

## Follow-on (after oversight)

1. Specialized Model Level 0 (local baseline on reviewed C7 exports)

## Blockers

None.
