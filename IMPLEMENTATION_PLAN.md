# Implementation Plan — XRV W3: Cross-Repo Readiness Portfolio + Pilot EERs

- Status: **COMPLETE**

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `xrv-portfolio-readiness` |
| Issue | [#266](https://github.com/loganware05/captains-compass-cursor/issues/266) |
| Baseline | **v1.84.0** @ `2016cd5` |
| Branch | `feature/266-xrv-portfolio-readiness` |
| Rollback | `rollback/pre-xrv-portfolio-readiness` @ `2016cd5` |
| Release | **v1.85.0** |
| Approved by | Logan Ware (Captain) — continue after #265 merge |
| Approval date | 2026-11-11 |
| Completed | 2026-11-11 |

## Outcome

1. Assess readiness against product repos (control-root imports/schema)
2. `profile=control|product` signal packs
3. Portfolio scorecard across pilot roots
4. EER fixtures for TrapHouse #37 and Bitcoin #18
5. W2 closeout docs; PrizePicksBot inventory handoff (plan-only)

## Acceptance

- [x] Product repo assess works without requiring orchestrator in product tree
- [x] Product profile scores NorthStar-installed product markers
- [x] Portfolio command emits multi-repo summary with locks false
- [x] Pilot EERs validate under EER gate
- [x] Doctor + tests + docs/ADR/VERSION 1.85.0

## Merged

[#267](https://github.com/loganware05/captains-compass-cursor/pull/267) @ `5c399ac` → **v1.85.0**.

## Follow-ons

- PrizePicksBot Pilot C onboard/baseline — **APPROVED**; product workstream
  ([`docs/plans/XRV_PILOT_C_PRIZEPICKS_BASELINE.md`](docs/plans/XRV_PILOT_C_PRIZEPICKS_BASELINE.md))
- TrapHouse ops-verified E2E (Captain-gated)
- Live trading / providers / live wagers remain denied
