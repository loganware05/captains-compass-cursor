# Implementation Plan — C1 Closeout + Hook Compat

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `c1-closeout-hook-compat` |
| Issue | [#201](https://github.com/loganware05/captains-compass-cursor/issues/201) |
| Notion | [Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.60.0** @ `2dbceea` |
| Branch | `fix/201-c1-closeout-hook-compat` |
| Rollback | `rollback/pre-c1-closeout-hook-compat` @ `2dbceea` |
| Release | **v1.60.1** |
| Captain | Logan Ware |
| Created | 2026-10-16 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-16 |
| Notes | Explicit “Approve c1-closeout”; standing order includes commit + open PR |

## Request

Finish C1 post-merge closeout: ship the live `plan-approval-check.sh` Python &lt;3.10 compatibility fix, reconcile project memory/README with v1.60.0 / #200, and document the Captain standing order that plan approval includes commit + PR creation.

## Acceptance Criteria

- [x] Hook contains `from __future__ import annotations` and parses under agent `python3`
- [x] Memory docs mark C1 shipped (#200 @ `2dbceea`)
- [x] README version matches VERSION (1.60.1)
- [x] Handbook standing order: approve → commit → open PR
- [x] Doctor + hook smoke
- [x] Evidence under `.agent/evidence/c1-closeout-hook-compat/`
- [ ] PR opened

## Non-Goals

C2–C7 product features (retrieval, difficulty, cycle, REA, routing, training).

## Rollback

`rollback/pre-c1-closeout-hook-compat` @ `2dbceea`
