# Implementation Plan — Specialized Model Level 1 (On-Device LoRA)

- Status: **APPROVED** (implementing)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `specialized-model-level-1` |
| Docs PR | [#231](https://github.com/loganware05/captains-compass-cursor/pull/231) |
| Notion | [Specialized Model — Mac M2 Training](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.69.0** @ `2507da6` (#231 merged) |
| Branch | `cursor/specialized-model-level-1-3ec1` |
| Rollback | `rollback/pre-specialized-model-level-1` @ `2507da6` |
| Release | **v1.70.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-21 |
| Notes | Standing order; defaults as written (reuse Level 0 gate; CI dry-run) |

## Acceptance Criteria

- [x] `specialized lora prepare|train|evaluate` runs when gated
- [x] Fail-closed without specialized-model gate
- [x] Dataset prepare consumes C7 export checklist; redaction preserved
- [x] Train does not commit weight/adapter binaries to this repo
- [x] Eval report compares to Level 0 baseline; `auto_promoted` false
- [x] Hermetic CI dry-run path; doctor + unit tests; evidence recorded
- [x] Docs/ADR/CHANGELOG; PR after approval (standing order)

## Open Questions (resolved)

1. Gate: reuse `COMPASS_SPECIALIZED_MODEL_ENABLED` — **yes**
2. CI train: dry-run + fixture adapter — **yes**
3. External trainer: `COMPASS_SPECIALIZED_LORA_TRAINER` — **yes**
4. Student shortlist: documented 0.5B–3B MLX; Captain picks at train time — **yes**

## Rollback Plan

Tag `rollback/pre-specialized-model-level-1` @ `2507da6`; revert PR.
Discard external adapter dirs separately (outside this repo).
