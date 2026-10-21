# Implementation Plan — Specialized Model Level 3 (Large Single GPU 48–80GB)

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `specialized-model-level-3` |
| Issue | *(Captain files before/on approval — agent cannot create GitHub issues)* |
| Notion | [Specialized Model — Mac M2 Training](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.71.0** @ `5727802` (#234 merged) |
| Proposed branch | `cursor/<issue>-specialized-model-level-3-3ec1` |
| Proposed rollback | `rollback/pre-specialized-model-level-3` @ `5727802` |
| Proposed release | **v1.72.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR |

## Request

Ship Specialized Model **Level 3** (Notion training ladder): **large single
GPU** (≈48–80GB VRAM) for 7B–14B adapters with longer context. After Level 2,
extend the gated GPU harness with a **job class** (`standard` vs `large`),
stricter cost acknowledgment for large-class submits, optional context/length
profile fields, and eval against Level 0–2 baselines — without multi-GPU
orchestration, weight commits, or auto-promotion.

## Problem Statement

Level 2 covers 16–24GB QLoRA jobs. Notion Level 3 is the next feasibility
tier when longer context or 7B–14B adapters need more VRAM. Without a distinct
job class + cost gate, large rentals risk being indistinguishable from Level 2
jobs and harder to audit.

## Desired Outcome

1. Extend gated `specialized gpu …` surface (reuse
   `COMPASS_SPECIALIZED_MODEL_ENABLED`):
   - `--class standard|large` on prepare/submit (default `standard`)
   - `large` documents 48–80GB / 7B–14B target class
2. Job manifest gains `job_class`, optional `max_seq_len` / `context_profile`
3. Non-dry-run submit still requires `--cost-ack`; large-class may require
   `--cost-ack-large` (or same `--cost-ack` with checklist field
   `large_class_cost_acknowledged`) — default **reuse `--cost-ack` + record
   `job_class` on the run**
4. Evaluate vs Level 0 baseline (+ Level 1/2 reference rates when present);
   extend `specialized-model-gpu-run` (or additive fields) with `job_class`
   - `weights_committed: false`, `auto_promoted: false`
5. Evidence under `.agent/evidence/specialized-model-level-3/`
6. Doctor + unit tests; CI hermetic (`--dry-run` only)
7. Docs: TESTING, ADR, CHANGELOG **v1.72.0**

## Acceptance Criteria

- [ ] `specialized gpu prepare|submit|evaluate` accepts `--class large`
- [ ] Fail-closed without specialized-model gate
- [ ] Non-dry-run submit requires cost acknowledgment (including large class)
- [ ] Job manifests record `job_class`; no weight binaries in this repo
- [ ] Eval report compares to Level 0 (+ L1/L2 refs); `auto_promoted` false
- [ ] Hermetic CI dry-run path; doctor + unit tests; evidence recorded
- [ ] Docs/ADR/CHANGELOG; PR after approval (standing order)

## Non-Goals

- Level 4+ multi-GPU / distributed training / research cluster
- Storing model weights or adapters in this repository
- Automatic promotion into Adaptive Intelligence routing
- Live GPU jobs inside GitHub Actions CI
- Provider marketplace integration beyond external runner contract
- Changing Level 2 default `standard` behavior beyond additive class field

## Assumptions

1. Level 2 GPU harness remains the base; Level 3 is primarily a class +
   profile extension.
2. Real large-GPU runs are Captain-operated via external runner; CI dry-run.
3. Approving Level 3 ships the harness; it does not authorize unbounded spend.

## Open Questions (defaults if approve as written)

1. **Surface:** extend existing `gpu` commands with `--class` → default **yes**
   (no new top-level verb).
2. **Cost ack:** reuse `--cost-ack` for both classes; record `job_class` →
   default **yes**.
3. **CI:** dry-run only → default **yes**.
4. **Schema:** extend Level 2 job/run schemas with optional `job_class`
   (default `standard`) → default **yes** (backward compatible).
5. **Large profile defaults in docs:** 7B–14B, 48–80GB, longer `max_seq_len`
   example → default **document; Captain picks instance at submit**.

## Current-State Analysis

| Asset | Role |
|---|---|
| `orchestrator/specialized/gpu.py` | Level 2 prepare/submit/evaluate |
| `.agent/specialized-gpu-jobs/` | GPU job manifests |
| Level 0–2 gold/eval paths | Baseline comparison |
| Notion Specialized Model page | Level 3–5 ladder |

## Proposed Architecture

```text
northstar specialized gpu --class large
        │
        ├── prepare  → job manifest with job_class=large
        ├── submit   → require --cost-ack; external runner or --dry-run
        └── evaluate → gold set vs L0 (+ L1/L2 refs)
                       write gpu-run report (auto_promoted=false)
```

## Workstreams

| ID | Scope |
|---|---|
| W1 | `job_class` + optional context profile on schemas/prepare |
| W2 | Submit/eval wiring + large-class dry-run fixtures |
| W3 | Unit tests + doctor |
| W4 | Docs / ADR / CHANGELOG |

## Files Expected to Change

- `orchestrator/specialized/gpu.py`
- `orchestrator/schemas/specialized-model-gpu-*.schema.json`
- `scripts/run-specialized-model.sh`, `scripts/northstar`, `scripts/doctor.sh`
- `tests/orchestrator/test_specialized_model_level_3.py`
- `tests/fixtures/specialized-model-gpu/` (large-class dry-run fixtures)
- `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md`
- `docs/plans/SPECIALIZED_MODEL_LEVEL_3.md`
- `.agent/evidence/specialized-model-level-3/`

## Testing Strategy

- Unit: fail-closed; cost-ack; `job_class=large` dry-run; no weight paths
- Regression: Level 0–2 tests still pass
- Doctor: schemas + fail-closed

## Security Review

- Reuse prior redaction/cost-ack patterns
- No live GPU in CI
- Never auto-promote adapters

## Rollback Plan

Tag `rollback/pre-specialized-model-level-3` @ `5727802`; revert PR.
Cancel/discard external GPU jobs outside this repo.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Untracked large-GPU spend | `--cost-ack`; dry-run default; no CI GPU |
| Schema break for Level 2 | Optional `job_class` defaulting to `standard` |
| Scope into multi-GPU | Hard Level 3 non-goal |

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 12 |
| Wall time | 8 hours |
| After approval | implement → validate → commit → open PR |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve specialized-model-level-3** (or revise open questions). After
approval, First Mate will branch, implement, validate, **commit, and open the PR**.
Merge remains yours. Please file a GitHub issue for tracking (agent cannot).

**Note:** Approving Level 3 ships the large-class harness; each non-dry-run
submit still requires `--cost-ack`.
