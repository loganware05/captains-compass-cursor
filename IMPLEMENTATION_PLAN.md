# Implementation Plan — E2E Cognitive Core Evaluation

- Status: **PR OPEN** ([#224](https://github.com/loganware05/captains-compass-cursor/pull/224))

## Metadata

| Field | Value |
|---|---|
| Status | **PR OPEN** ([#224](https://github.com/loganware05/captains-compass-cursor/pull/224)) |
| Plan ID | `e2e-cognitive-core-evaluation` |
| Issue | [#222](https://github.com/loganware05/captains-compass-cursor/issues/222) |
| Notion | [Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.66.1** @ `bb1b5b9` (#223 merged) |
| Branch | `cursor/222-e2e-cognitive-core-evaluation-3ec1` |
| Rollback | `rollback/pre-e2e-cognitive-core-evaluation` @ `bb1b5b9` |
| Release | **v1.67.0** |
| Captain | Logan Ware |
| Created | 2026-10-20 |
| Approved | 2026-10-20 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-10-20 |
| Notes | Standing-order approval: “I approve e2e-cognitive-core-evaluation”; #223 merged. |

## Request

Ship a bounded hermetic C1–C7 Cognitive Core e2e harness with schema-validated
report, doctor checks, and measured baselines. Sandbox mode optional; no new
authority.

## Acceptance Criteria

- [x] Hermetic e2e harness runs green offline (`./scripts/run-cognitive-core-e2e.sh --enable-gates`)
- [x] Report schema validates; authority flags always false
- [x] Baselines written under `.agent/evidence/e2e-cognitive-core-evaluation/`
- [x] Fail-closed without required `COMPASS_*_ENABLED` flags
- [x] Optional sandbox mode documented (`--mode sandbox`)
- [x] Doctor + unit tests; offline default
- [x] Docs/ADR/CHANGELOG; PR opened after approval (standing order)

## Non-Goals

Persistent oversight automation; Specialized Model fine-tuning; HTTP `/v1/*`;
live embeddings/REA required for CI.

## Rollback Plan

Tag `rollback/pre-e2e-cognitive-core-evaluation` @ `bb1b5b9`; revert PR.
