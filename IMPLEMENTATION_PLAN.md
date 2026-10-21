# Implementation Plan — Specialized Model Level 0 (Local Baseline)

- Status: **APPROVED** (implementing)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `specialized-model-level-0` |
| Issue | [#228](https://github.com/loganware05/captains-compass-cursor/issues/228) |
| Docs PR | [#229](https://github.com/loganware05/captains-compass-cursor/pull/229) |
| Notion | [Specialized Model — Mac M2 Training](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.68.0** @ `6ffa7c7` (#229 merged; #227 oversight) |
| Branch | `cursor/228-specialized-model-level-0-3ec1` |
| Rollback | `rollback/pre-specialized-model-level-0` @ `6ffa7c7` |
| Release | **v1.69.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-21 |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR; defaults as written |

## Request

Ship Specialized Model **Level 0** (Notion training ladder): **no fine-tuning**.
Provide a gated local baseline harness that (1) freezes a held-out evaluation
gold set, (2) scores retrieval + prompt baselines (and an optional local student
inference stub), (3) consumes permission-checked C7 training-export manifests,
and (4) records license/redaction/provenance + go/no-go evidence — without
training weights, uploading data, or auto-promoting models.

## Acceptance Criteria

- [x] `specialized baseline` runs hermetically when gated
- [x] Fail-closed without `COMPASS_SPECIALIZED_MODEL_ENABLED`
- [x] Gold set fixture present; baseline report schema-validated
- [x] `weights_trained` and `auto_uploaded` always false
- [x] Can attach/score against a C7 export (fixture OK)
- [x] Doctor + unit tests; evidence recorded
- [x] Docs/ADR/CHANGELOG; PR after approval (standing order)

## Non-Goals

- Level 1+ LoRA/QLoRA / MLX training runs
- Storing model weights or adapters in this repository
- Automatic model promotion into Adaptive Intelligence routing
- Training current repository HEAD into weights as a substitute for retrieval
- Live GPU rental / cloud training jobs
- Expanding C7 export authority

## Open Questions (resolved)

1. CI student: fixture stub only — **yes**
2. Gold-set size for v1.69.0: **24**
3. Package layout: thin `orchestrator/specialized/` in-repo — **yes**

## Rollback Plan

Tag `rollback/pre-specialized-model-level-0` @ `6ffa7c7`; revert PR.

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 10 |
| Wall time | 6 hours |
| After approval | implement → validate → commit → open PR |
