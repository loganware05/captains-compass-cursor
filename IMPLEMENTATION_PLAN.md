# Implementation Plan — XRV W2: Eight-Pillar Readiness Assessor

- Status: **COMPLETE** (PR open)

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** (PR [#265](https://github.com/loganware05/captains-compass-cursor/pull/265)) |
| Plan ID | `xrv-readiness-assessor` |
| Issue | [#263](https://github.com/loganware05/captains-compass-cursor/issues/263) |
| Baseline | **v1.83.1** @ `cb85c4a` |
| Branch | `feature/263-xrv-readiness-assessor` |
| Rollback | `rollback/pre-xrv-readiness-assessor` @ `cb85c4a` |
| Proposed release | **v1.84.0** |
| Program | Cross-Repository Validation (XRV) |
| Prior | W1 `xrv-release-integrity` (#261/#262) **COMPLETE** |
| Approved by | Logan Ware (Captain) — “Approve xrv-readiness-assessor as written” |
| Approval date | 2026-11-11 |

## Desired Outcome

Gated hermetic `northstar assess readiness` with dual score sections
(repository readiness vs NorthStar effectiveness), schema locks, doctor
fail-closed, fixtures + tests. No invented scores.

## Acceptance Criteria

- [x] Fail-closed without `COMPASS_XRV_READINESS_ENABLED`
- [x] Dual sections; missing evidence → unscored (not invented)
- [x] Authority locks const false
- [x] Doctor + unit tests + docs/ADR/VERSION 1.84.0

## Autonomy Budget

See `.agent/budgets/xrv-readiness-assessor.md`.
