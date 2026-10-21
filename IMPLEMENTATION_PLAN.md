# Implementation Plan — Read-Only Persistent Oversight

- Status: **PR OPEN** ([#227](https://github.com/loganware05/captains-compass-cursor/pull/227))

## Metadata

| Field | Value |
|---|---|
| Status | **PR OPEN** ([#227](https://github.com/loganware05/captains-compass-cursor/pull/227)) |
| Plan ID | `read-only-persistent-oversight` |
| Issue | [#225](https://github.com/loganware05/captains-compass-cursor/issues/225) |
| Notion | [Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.67.0** @ `c5d435e` (#226 merged) |
| Branch | `cursor/225-read-only-persistent-oversight-3ec1` |
| Rollback | `rollback/pre-read-only-persistent-oversight` @ `c5d435e` |
| Release | **v1.68.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |
| Approved | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-10-21 |
| Notes | Standing-order approval: “approve read-only-persistent-oversight”; #226 merged. |

## Request

Opt-in post-merge / on-demand oversight composer over brain sync + Overseer
snapshot/compare/reconcile — proposal-only.

## Acceptance Criteria

- [x] `oversight run` composes snapshot/compare/reconcile when gated
- [x] Fail-closed without required enable flags
- [x] Reconcile proposals never set `applied` / authority flags true
- [x] Optional brain sync only when `COMPASS_BRAIN_ENABLED=1`
- [x] Hermetic tests + doctor; evidence recorded
- [x] Docs/ADR/CHANGELOG; PR opened (standing order)

## Rollback Plan

Tag `rollback/pre-read-only-persistent-oversight` @ `c5d435e`; revert PR.
