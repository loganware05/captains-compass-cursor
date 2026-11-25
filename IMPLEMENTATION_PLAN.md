# Implementation Plan — XRV Ops Live-Local Smoke

- Status: **COMPLETE**

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain |
| Approved at | 2026-11-25 |
| Defaults | Q1=yes → v1.96.0; Q2=live_deploy=false; Q3=doctor+reconstruct only; Q4=defer Bend/#237 |
| Issue | [#316](https://github.com/loganware05/captains-compass-cursor/issues/316) |
| Rollback | `rollback/pre-xrv-ops-live-local` @ `08c897f` |
| Branch | `feature/316-xrv-ops-live-local` |
| Worktree | `/Users/loganware/Documents/Personal/Code/captains-compass-xrv-live-local` |

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `xrv-ops-live-local` |
| Issue | [#316](https://github.com/loganware05/captains-compass-cursor/issues/316) |
| Proposed release | **v1.96.0** |
| Baseline | `origin/main` @ `08c897f` / **v1.95.0** (closeout [#315](https://github.com/loganware05/captains-compass-cursor/pull/315) merged) |
| Rollback | `rollback/pre-xrv-ops-live-local` @ `08c897f` |
| Prior | Hermetic ops-verified shipped **v1.94.0**; live production deploy still deferred |

Budget: `.agent/budgets/xrv-ops-live-local.md`  
Durable copy: `docs/plans/XRV_OPS_LIVE_LOCAL.md`

## Goal

Promote XRV ops-verified from fixture-padded SHAs to a **local operational smoke** against a real control-repo tip: doctor + `evidence reconstruct` + EER `ops_verification` with authentic `repository_sha`. Still **no production deploy** (`live_deploy=false` unless Captain opts in).

## In scope

1. Local smoke script/CLI path recording doctor + reconstruct against tip SHA
2. EER fixture/evidence with real `repository_sha` and `ops_verification.live_deploy=false`
3. Docs / doctor surface / tests / VERSION **v1.96.0**

## Out of scope

- Production / remote live deploy (`live_deploy=true`)
- Auto-merge or authority mutation
- Specialized Level 3 (#237)
- Enabling `COMPASS_BEND_STRICT_LAWS_CI` (Captain ops)

## Acceptance criteria

- [x] Local smoke produces ops-verified EER bound to real tip SHA
- [x] `live_deploy` remains false by default
- [x] Hermetic/unit tests + doctor green
- [x] Authority locks remain false

## Approval Boundary

**Approved.** Implementation in progress under autonomy budget `xrv-ops-live-local`.


## Completion

| Field | Value |
|---|---|
| Completed at | 2026-11-25 |
| Proposed version | **v1.96.0** |
| Validation | `test_xrv_ops_live_local` + live-local-316 smoke (doctor+reconstruct) |
| Production deploy | Deferred (`live_deploy=false`) |
