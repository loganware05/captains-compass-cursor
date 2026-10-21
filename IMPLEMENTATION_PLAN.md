# Implementation Plan — Specialized Model Level 2 (Single Rented GPU QLoRA)

- Status: **APPROVED** (implementing)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `specialized-model-level-2` |
| Docs PR | [#233](https://github.com/loganware05/captains-compass-cursor/pull/233) |
| Notion | [Specialized Model — Mac M2 Training](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.70.0** @ `e5256f1` (#233 merged) |
| Branch | `cursor/specialized-model-level-2-3ec1` |
| Rollback | `rollback/pre-specialized-model-level-2` @ `e5256f1` |
| Release | **v1.71.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-21 |
| Notes | Standing order; defaults as written (cost-ack; CI dry-run) |

## Acceptance Criteria

- [x] `specialized gpu prepare|submit|evaluate` runs when gated
- [x] Fail-closed without specialized-model gate
- [x] Non-dry-run submit requires cost acknowledgment
- [x] Train/submit does not commit weight/adapter binaries to this repo
- [x] Eval report compares to Level 0 (+ optional Level 1); `auto_promoted` false
- [x] Hermetic CI dry-run path; doctor + unit tests; evidence recorded
- [x] Docs/ADR/CHANGELOG; PR after approval (standing order)

## Open Questions (resolved)

1. Gate: reuse `COMPASS_SPECIALIZED_MODEL_ENABLED` — **yes**
2. CI: dry-run only — **yes**
3. Cost ack: `--cost-ack` for non-dry-run — **yes**
4. External runner: `COMPASS_SPECIALIZED_GPU_RUNNER` — **yes**
5. Target class: 3B–8B QLoRA / 16–24GB documented — **yes**

## Rollback Plan

Tag `rollback/pre-specialized-model-level-2` @ `e5256f1`; revert PR.
Cancel/discard external GPU jobs and adapter dirs outside this repo.
