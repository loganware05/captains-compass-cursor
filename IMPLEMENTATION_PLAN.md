# Implementation Plan — Specialized Model Level 1 (On-Device LoRA)

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `specialized-model-level-1` |
| Issue | *(Captain files before/on approval — agent cannot create GitHub issues)* |
| Docs PR | [#231](https://github.com/loganware05/captains-compass-cursor/pull/231) |
| Notion | [Specialized Model — Mac M2 Training](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.69.0** @ `e04169d` (#230 merged) |
| Proposed branch | `cursor/<issue>-specialized-model-level-1-3ec1` |
| Proposed rollback | `rollback/pre-specialized-model-level-1` @ `e04169d` |
| Proposed release | **v1.70.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR |

## Request

Ship Specialized Model **Level 1** (Notion training ladder): **on-device LoRA**.
After Level 0 baseline, provide a gated control-repo harness that (1) prepares a
permission-checked training dataset from C7 reviewed exports, (2) launches or
records an **external** MLX/MLX-LM LoRA train run (weights outside this repo),
(3) evaluates adapter vs Level 0 baseline on the held-out gold set, and
(4) writes a schema-validated run manifest with license/redaction/provenance and
go/no-go — without auto-promoting adapters into Adaptive Intelligence routing.

## Problem Statement

Level 0 can score retrieval/prompt/stub baselines and attach C7 exports, but
there is no governed path to run a small on-device LoRA experiment and compare
it to that baseline. Notion Level 1 requires holdout retention, rollback, and
cost/quality tracking before any rented-GPU work (Level 2+).

## Desired Outcome

1. Gated surface (default off; reuse `COMPASS_SPECIALIZED_MODEL_ENABLED` or
   add `COMPASS_SPECIALIZED_LORA_ENABLED` — default **reuse Level 0 gate**):
   - `./scripts/run-specialized-model.sh lora prepare|train|evaluate …`
   - `northstar specialized lora …`
2. Dataset prepare from C7 export(s) → versioned dataset manifest under
   `.agent/specialized-datasets/` (JSON/metadata only; large blobs optional
   external path via env)
3. Train step: invoke external trainer via `COMPASS_SPECIALIZED_LORA_TRAINER`
   (script/path) or `--dry-run` fixture; **never** write `.safetensors` /
   adapter weights into the control repo
4. Evaluate: compare Level 0 baseline scores vs adapter-backed stub/live
   student on gold set; schema `specialized-model-lora-run`
   - `weights_committed: false`, `auto_promoted: false`, authority flags false
5. Evidence under `.agent/evidence/specialized-model-level-1/`
6. Doctor + unit tests; CI hermetic (`--dry-run` / fixture adapter only)
7. Docs: TESTING, ADR, CHANGELOG **v1.70.0**; weights-outside-repo note

## Acceptance Criteria

- [ ] `specialized lora prepare|train|evaluate` runs when gated
- [ ] Fail-closed without specialized-model gate
- [ ] Dataset prepare consumes C7 export checklist; redaction preserved
- [ ] Train does not commit weight/adapter binaries to this repo
- [ ] Eval report compares to Level 0 baseline; `auto_promoted` false
- [ ] Hermetic CI dry-run path; doctor + unit tests; evidence recorded
- [ ] Docs/ADR/CHANGELOG; PR after approval (standing order)

## Non-Goals

- Level 2+ rented GPU / multi-GPU / research-cluster training
- Storing model weights or adapters in this repository
- Automatic promotion into Adaptive Intelligence routing
- Expanding gold set to Notion’s full 100–500 (may grow modestly; not required)
- Live training inside GitHub Actions CI
- Preference/RLHF loops; Kimi K3 distillation (optional later, license-gated)

## Assumptions

1. Level 0 baseline harness remains the comparison baseline.
2. Real LoRA train runs on Captain’s Mac (MLX/MLX-LM); CI uses dry-run/fixtures.
3. Initial dataset size may be well below Notion’s 200–1,000 aspirational range
   if C7 reviewed volume is smaller — plan ships the harness; Captain supplies
   volume over time.

## Open Questions (defaults if approve as written)

1. **Gate:** reuse `COMPASS_SPECIALIZED_MODEL_ENABLED` → default **yes**
   (document LoRA subcommands under same gate).
2. **CI train:** dry-run + fixture adapter only → default **yes**.
3. **External trainer contract:** env
   `COMPASS_SPECIALIZED_LORA_TRAINER` pointing to a script that accepts a
   dataset manifest path and writes an adapter dir + train metrics JSON →
   default **yes**.
4. **Student size shortlist for docs:** 0.5B–3B MLX-compatible → default
   **document two candidates; Captain picks at train time**.

## Current-State Analysis

| Asset | Role |
|---|---|
| `orchestrator/specialized/` | Level 0 baseline (v1.69.0) |
| `orchestrator/train_bridge/` | C7 reviewed export manifests |
| `tests/fixtures/specialized-model-gold/` | Held-out eval gold set |
| Notion Specialized Model page | Level 1–5 ladder + Mac constraints |

## Proposed Architecture

```text
northstar specialized lora
        │
        ├── prepare  → dataset manifest from C7 export(s)
        ├── train    → external trainer (or --dry-run fixture)
        └── evaluate → gold set: Level 0 baseline vs adapter
                       write lora-run report (auto_promoted=false)
```

## Workstreams

| ID | Scope |
|---|---|
| W1 | Dataset prepare + schemas (`specialized-model-dataset`, `specialized-model-lora-run`) |
| W2 | External trainer contract + dry-run fixture + CLI/northstar |
| W3 | Eval vs Level 0 baseline; unit tests; doctor |
| W4 | Docs / ADR / CHANGELOG / weights-outside-repo note |

## Files Expected to Change

- `orchestrator/specialized/` (lora prepare/train/evaluate)
- `orchestrator/schemas/specialized-model-*.schema.json`
- `scripts/run-specialized-model.sh`, `scripts/northstar`, `scripts/doctor.sh`
- `tests/orchestrator/test_specialized_model_level_1.py`
- `tests/fixtures/specialized-model-lora/` (dry-run fixtures)
- `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md`
- `docs/plans/SPECIALIZED_MODEL_LEVEL_1.md`
- `.agent/evidence/specialized-model-level-1/`

## Testing Strategy

- Unit: fail-closed; no weight paths under repo; dry-run train; eval schema locks
- Hermetic prepare+train+evaluate offline
- Regression: Level 0 baseline tests still pass
- Doctor: schemas + script + fail-closed

## Security Review

- Reuse C7 redaction; never embed secrets in datasets committed here
- No network model download required in default CI path
- Never auto-promote adapters into routing

## Rollback Plan

Tag `rollback/pre-specialized-model-level-1` @ `e04169d`; revert PR.
Discard external adapter dirs separately (outside this repo).

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Weights accidentally committed | Doctor deny-list; docs; `.gitignore` patterns for common weight suffixes |
| Scope into Level 2 GPU rental | Hard non-goal |
| Thin C7 dataset | Harness ships; volume is Captain-owned; eval still requires holdout |

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 12 |
| Wall time | 8 hours |
| After approval | implement → validate → commit → open PR |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve specialized-model-level-1** (or revise open questions). After
approval, First Mate will branch, implement, validate, **commit, and open the PR**.
Merge remains yours. Please file a GitHub issue for tracking (agent cannot).
