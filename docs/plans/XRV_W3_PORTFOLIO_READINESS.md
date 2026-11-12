# XRV W3 — Cross-Repo Readiness Portfolio + Pilot EERs

> **COMPLETE** — [#266](https://github.com/loganware05/captains-compass-cursor/issues/266) /
> [#267](https://github.com/loganware05/captains-compass-cursor/pull/267) → **v1.85.0** @ `5c399ac`.
> Rollback: `rollback/pre-xrv-portfolio-readiness` @ `2016cd5`.
> Follow-on: [`XRV_PILOT_C_PRIZEPICKS_BASELINE.md`](XRV_PILOT_C_PRIZEPICKS_BASELINE.md).

## Operator surfaces

```bash
COMPASS_XRV_READINESS_ENABLED=1 \
  ./scripts/northstar assess readiness --profile product --repo /path/to/product

COMPASS_XRV_READINESS_ENABLED=1 \
  ./scripts/northstar assess portfolio \
  --repo northstar=. \
  --repo traphouse=/Users/loganware/TrapHouseKitchen \
  --repo bitcoin=/Users/loganware/bitcoin-data-collector \
  --repo prizepicks=/Users/loganware/Documents/Personal/Code/PrizePicksBot
```

Local smoke at merge: northstar/traphouse/bitcoin `ready`/`effective`; locks false.

## Pilot EERs

- `.agent/evidence/xrv/eer-traphouse-slice17-reconcile.json` (PR #37)
- `.agent/evidence/xrv/eer-bitcoin-pilot-b-continuity.json` (PR #18)
