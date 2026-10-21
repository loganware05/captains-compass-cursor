# Implementation Plan — Specialized Model Level 2 (Single Rented GPU QLoRA)

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `specialized-model-level-2` |
| Issue | *(Captain files before/on approval — agent cannot create GitHub issues)* |
| Docs PR | [#233](https://github.com/loganware05/captains-compass-cursor/pull/233) |
| Notion | [Specialized Model — Mac M2 Training](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.70.0** @ `d76ebd0` (#232 merged) |
| Proposed branch | `cursor/<issue>-specialized-model-level-2-3ec1` |
| Proposed rollback | `rollback/pre-specialized-model-level-2` @ `d76ebd0` |
| Proposed release | **v1.71.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR |

## Request

Ship Specialized Model **Level 2** (Notion training ladder): **single rented
GPU QLoRA** (≈16–24GB VRAM, 3B–8B students). After Level 1, provide a gated
control-repo harness that (1) prepares a GPU job manifest from an existing
Level 1 dataset, (2) requires explicit Captain **cost acknowledgment**,
(3) submits or records an **external** GPU train job (weights outside this
repo), (4) evaluates the resulting adapter vs Level 0/1 baselines on the
held-out gold set, and (5) writes a schema-validated run report with
license/redaction/provenance and go/no-go — without auto-promoting adapters.

## Problem Statement

Level 1 supports on-device LoRA with dry-run CI, but Mac 16GB unified memory
limits context, batch, and model size. Notion Level 2 is the next feasibility
tier when Level 1 hits memory/throughput limits and ROI justifies rental.
Without a governed cost-ack + remote job contract, GPU experiments risk
untracked spend and weight leakage into the control repo.

## Desired Outcome

1. Gated surface (reuse `COMPASS_SPECIALIZED_MODEL_ENABLED`):
   - `./scripts/run-specialized-model.sh gpu prepare|submit|evaluate …`
   - `northstar specialized gpu …`
2. Job prepare from Level 1 dataset → `.agent/specialized-gpu-jobs/` metadata
3. Submit requires `--cost-ack` (and/or checklist field `cost_acknowledged`)
   plus external runner `COMPASS_SPECIALIZED_GPU_RUNNER` or `--dry-run`
4. Evaluate: compare gold-set scores vs Level 0 baseline (+ Level 1 dry-run
   rates when available); schema `specialized-model-gpu-run`
   - `weights_committed: false`, `auto_promoted: false`, authority flags false
   - `cost_acknowledged: true` required for non-dry-run submit
5. Evidence under `.agent/evidence/specialized-model-level-2/`
6. Doctor + unit tests; CI hermetic (`--dry-run` only — no live GPU in CI)
7. Docs: TESTING, ADR, CHANGELOG **v1.71.0**; cost + weights-outside-repo notes

## Acceptance Criteria

- [ ] `specialized gpu prepare|submit|evaluate` runs when gated
- [ ] Fail-closed without specialized-model gate
- [ ] Non-dry-run submit requires cost acknowledgment
- [ ] Train/submit does not commit weight/adapter binaries to this repo
- [ ] Eval report compares to Level 0 (+ optional Level 1); `auto_promoted` false
- [ ] Hermetic CI dry-run path; doctor + unit tests; evidence recorded
- [ ] Docs/ADR/CHANGELOG; PR after approval (standing order)

## Non-Goals

- Level 3+ 48–80GB / multi-GPU / research-cluster training
- Storing model weights or adapters in this repository
- Automatic promotion into Adaptive Intelligence routing
- Live GPU jobs inside GitHub Actions CI
- Provider marketplace integration beyond an external runner contract
- Expanding gold set to Notion’s full 100–500 (not required for v1.71.0)

## Assumptions

1. Level 1 harness remains available; Level 2 reuses its datasets + gold set.
2. Real GPU runs are Captain-operated via external runner; CI uses dry-run.
3. Proceeding to Level 2 implies Captain judges Level 1 limits + ROI — this plan
   does not auto-decide that; the plan ships the harness.

## Open Questions (defaults if approve as written)

1. **Gate:** reuse `COMPASS_SPECIALIZED_MODEL_ENABLED` → default **yes**
2. **CI:** dry-run job manifest + fixture metrics only → default **yes**
3. **Cost ack:** required CLI flag `--cost-ack` for non-dry-run submit →
   default **yes**
4. **External runner:** env `COMPASS_SPECIALIZED_GPU_RUNNER` accepting job
   manifest path + writing adapter dir + metrics JSON outside repo →
   default **yes**
5. **Target class in docs:** 3B–8B QLoRA on 16–24GB VRAM → default **document;
   Captain picks provider/instance at submit time**

## Current-State Analysis

| Asset | Role |
|---|---|
| `orchestrator/specialized/lora.py` | Level 1 prepare/train/evaluate |
| `.agent/specialized-datasets/` | Level 1 dataset manifests |
| `tests/fixtures/specialized-model-gold/` | Held-out eval gold set |
| Notion Specialized Model page | Level 2–5 ladder + cost caution |

## Proposed Architecture

```text
northstar specialized gpu
        │
        ├── prepare  → GPU job manifest from Level 1 dataset
        ├── submit   → require --cost-ack; external runner or --dry-run
        └── evaluate → gold set vs Level 0/1 baselines
                       write gpu-run report (auto_promoted=false)
```

## Workstreams

| ID | Scope |
|---|---|
| W1 | Job manifest schema + prepare from Level 1 dataset |
| W2 | Submit + cost-ack + external runner / dry-run |
| W3 | Evaluate vs baselines; unit tests; doctor |
| W4 | Docs / ADR / CHANGELOG / cost + weights-outside-repo notes |

## Files Expected to Change

- `orchestrator/specialized/` (gpu prepare/submit/evaluate)
- `orchestrator/schemas/specialized-model-gpu-*.schema.json`
- `scripts/run-specialized-model.sh`, `scripts/northstar`, `scripts/doctor.sh`
- `tests/orchestrator/test_specialized_model_level_2.py`
- `tests/fixtures/specialized-model-gpu/` (dry-run fixtures)
- `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md`
- `docs/plans/SPECIALIZED_MODEL_LEVEL_2.md`
- `.agent/evidence/specialized-model-level-2/`

## Testing Strategy

- Unit: fail-closed; cost-ack required; no weight paths under repo; dry-run
- Hermetic prepare+submit+evaluate offline
- Regression: Level 0/1 tests still pass
- Doctor: schemas + script + fail-closed

## Security Review

- Reuse C7/Level 1 redaction; never embed secrets in job manifests
- No live GPU or network model download required in default CI
- Never auto-promote adapters into routing
- Cost ack is an operator attestation, not a payment integration

## Rollback Plan

Tag `rollback/pre-specialized-model-level-2` @ `d76ebd0`; revert PR.
Cancel/discard external GPU jobs and adapter dirs outside this repo.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Untracked cloud spend | Require `--cost-ack`; dry-run default; no CI GPU |
| Weights committed | Existing gitignore + doctor refuse patterns |
| Scope into multi-GPU | Hard Level 2 non-goal |

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 12 |
| Wall time | 8 hours |
| After approval | implement → validate → commit → open PR |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve specialized-model-level-2** (or revise open questions). After
approval, First Mate will branch, implement, validate, **commit, and open the PR**.
Merge remains yours. Please file a GitHub issue for tracking (agent cannot).

**Note:** Approving Level 2 ships the harness; it does not authorize unbounded
GPU spend. Each non-dry-run submit still requires `--cost-ack`.
