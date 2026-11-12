# XRV W3 — Cross-Repo Readiness Portfolio + Pilot EERs

> **IN PROGRESS** — [#266](https://github.com/loganware05/captains-compass-cursor/issues/266) → **v1.85.0**.
> Rollback: `rollback/pre-xrv-portfolio-readiness` @ `2016cd5`.

## Operator surfaces

```bash
COMPASS_XRV_READINESS_ENABLED=1 \
  ./scripts/northstar assess readiness --profile product --repo /path/to/product

COMPASS_XRV_READINESS_ENABLED=1 \
  ./scripts/northstar assess portfolio \
  --repo northstar=. \
  --repo traphouse=/Users/loganware/TrapHouseKitchen \
  --repo bitcoin=/Users/loganware/bitcoin-data-collector
```

Local smoke (2026-11-11): all three `ready`/`effective`; locks false.

## Pilot EERs

- `.agent/evidence/xrv/eer-traphouse-slice17-reconcile.json` (PR #37)
- `.agent/evidence/xrv/eer-bitcoin-pilot-b-continuity.json` (PR #18)
