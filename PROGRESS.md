# Progress

## Current status

**IN PROGRESS:** [#266](https://github.com/loganware05/captains-compass-cursor/issues/266) /
PR [#267](https://github.com/loganware05/captains-compass-cursor/pull/267)
`xrv-portfolio-readiness` on `feature/266-xrv-portfolio-readiness` → **v1.85.0**.

| Item | Value |
|---|---|
| Baseline | **v1.84.0** @ `2016cd5` |
| Active plan | `xrv-portfolio-readiness` **APPROVED** |
| Issue | [#266](https://github.com/loganware05/captains-compass-cursor/issues/266) |
| Rollback | `rollback/pre-xrv-portfolio-readiness` @ `2016cd5` |

### Prior closeout

- W2 readiness assessor merged [#265](https://github.com/loganware05/captains-compass-cursor/pull/265); #263 closed
- TrapHouse Pilot A reconcile [#37](https://github.com/loganware05/TrapHouseKitchen/pull/37) merged
- Bitcoin Pilot B [#18](https://github.com/loganware05/bitcoin-data-collector/pull/18) merged

## Standing order

Approve ⇒ implement → validate → commit → open PR. Merge remains Captain-only.

## Validation (local)

- XRV unit tests: pass
- `./scripts/doctor.sh`: pass
- `./tests/run.sh`: 125 passed, 0 failed
- Portfolio smoke: northstar/traphouse/bitcoin all ready/effective; locks false
- PrizePicksBot Pilot C inventory handoff launched (plan-only)

## Blockers

None.
