# Implementation Plan — C7 Cognitive Core Training Bridge

- Status: **PR OPEN** ([#219](https://github.com/loganware05/captains-compass-cursor/pull/219))

## Metadata

| Field | Value |
|---|---|
| Status | **PR OPEN** ([#219](https://github.com/loganware05/captains-compass-cursor/pull/219)) |
| Plan ID | `c7-cognitive-core-training-bridge` |
| Issue | [#217](https://github.com/loganware05/captains-compass-cursor/issues/217) |
| Notion | [Cognitive Core — C7 Training bridge](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.65.0** @ `f16e8bb` (C6 closeout #218) |
| Branch | `cursor/217-c7-training-bridge-64df` |
| Rollback | `rollback/pre-c7-cognitive-core-training-bridge` @ `f16e8bb` |
| Release | **v1.66.0** (proposed) |
| Captain | Logan Ware |
| Created | 2026-10-19 |
| Approved | 2026-10-19 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-10-19 |
| Notes | Standing-order approval: “I approve c7-cognitive-core-training-bridge”. Completes Cognitive Core C1–C7 track. |

## Request

Ship Cognitive Core **C7 — Training bridge**: a feature-gated exporter that packages **permission-checked, reviewed** trajectories (from Experiences and/or closed cycles) into a Specialized Model dataset hand-off manifest. Include redaction, provenance citations, and a Captain Learning/Promotion review packet. Gate any hand-off on independent eval + security + Captain approval. Never change live model weights, auto-upload, or expand authority.

## Problem Statement

Notion separates ownership: Specialized Model owns experimentation/weights/datasets; Cognitive Core owns Adaptive Intelligence and governed export of reviewed trajectories. NorthStar already records Experiences (`orchestrator/telemetry`), cycle close drafts (C4), and Experience→Skill drafts (`orchestrator/training/from_experience.py`), but lacks a Cognitive Core–owned, SHA-cited **dataset export bridge** with explicit permission checks and promotion gates before Specialized Model ingest.

## Desired Outcome

```bash
COMPASS_TRAIN_BRIDGE_ENABLED=1 \
./scripts/northstar train export \
  --from experiences|cycles \
  [--plan-id ID] \
  [--out PATH] \
  --repo PATH

COMPASS_TRAIN_BRIDGE_ENABLED=1 \
./scripts/northstar train review --export-id ID --repo PATH
```

Returns schema-validated JSON:

- **export** — manifest of trajectory records (redacted), permission checklist, source SHAs/Experience/cycle ids, dataset schema version; `approved_for_execution: false` / `authority_mutation: false` / `auto_uploaded: false`
- **review** — Captain-facing packet listing export readiness, eval/security checklist status, and required approvals before Specialized Model ingest

Default path is **hermetic/local** (writes under `.agent/training-exports/`). No live training or remote upload in CI.

### Governance (Notion-aligned)

1. Only include trajectories marked reviewed / eligible (explicit flags or Captain-approved Experiences)
2. Permission checklist (license/PII/secret redaction/export authorized)
3. Independent eval + security review fields required before “ready for Specialized Model”
4. Captain approval required for promotion/hand-off
5. No automatic live weight changes or autonomous merges

## Acceptance Criteria

- [x] Gated `northstar train export` and `northstar train review` (fail-closed when enable flag unset)
- [x] Schema(s) for training-export manifest + review packet with authority flags const false; `auto_uploaded: false`
- [x] Export redacts secrets/sensitive paths; cites repository SHA + source Experience/cycle ids
- [x] Permission checklist required; incomplete → refuse export or mark not-ready
- [x] Hermetic fixture mode for CI (no live training/upload)
- [x] Distinct from Experience→Skill draft path (`orchestrator/training/from_experience.py`) — may cite it; must not auto-promote Skills or weights
- [x] Doctor + unit tests green; evidence under `.agent/evidence/c7-cognitive-core-training-bridge/`
- [x] Memory docs + CHANGELOG + VERSION **v1.66.0**; ADR-084
- [x] PR opened (standing order after approval)

## Non-Goals

- Training or fine-tuning models inside NorthStar
- Auto-upload to external dataset registries
- Automatic weight/adapter promotion
- Replacing Specialized Model ownership of datasets/weights
- Expanding Captain approval gates
- HTTP training API
- External cognitive-core package extract

## Affected systems

| Area | Change |
|---|---|
| `orchestrator/train_bridge/` (new) | Export + review services |
| `orchestrator/schemas/` | `training-export-manifest` / `training-export-review` |
| Existing | Read Experiences / cycle state; cite `from_experience` |
| `scripts/` | `run-train-bridge.sh` + `northstar train` wiring |
| `scripts/doctor.sh` | schema + fail-closed smoke |
| Tests / fixtures | Hermetic export/review |
| Project memory | PLAN / PROGRESS / CHANGELOG / DECISIONS / TESTING / VERSION |

## Workstreams

1. Schema + permission checklist + redaction helpers
2. Hermetic export from fixture Experiences/cycles
3. Review packet + CLI/launcher/doctor
4. Docs / evidence / release bump (Cognitive Core C1–C7 complete)

## Validation

- Doctor; unit + hermetic export tests
- Security: redaction; no auto-upload; no authority expansion
- Rollback tag before implementation

## Autonomy Budget

| Limit | Value |
|---|---|
| Maximum iterations | 10 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 300 |
| Maximum estimated cost (USD) | 0 |
| Stop on scope change | true |

## Rollback

Tag `rollback/pre-c7-cognitive-core-training-bridge` @ `f16e8bb` (pre-implementation).

## Definition of Done

Acceptance criteria checked; evidence recorded; PR open; First Mate inspected.

## Prior closeout (C6)

C6 REA deep analysis **COMPLETE** — merged [#216](https://github.com/loganware05/captains-compass-cursor/pull/216) → `main` @ `1308b5f` (**v1.65.0**); closeout [#218](https://github.com/loganware05/captains-compass-cursor/pull/218) @ `f16e8bb`. Plan ID `c6-cognitive-core-rea-deep-analysis`. Issue #214 closed.
