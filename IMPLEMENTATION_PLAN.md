# Implementation Plan — Specialized Model Level 0 (Local Baseline)

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `specialized-model-level-0` |
| Issue | [#228](https://github.com/loganware05/captains-compass-cursor/issues/228) |
| Notion | [Specialized Model — Mac M2 Training](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.68.0** @ `f5bbf24` (#227 merged) |
| Proposed branch | `cursor/228-specialized-model-level-0-3ec1` |
| Proposed rollback | `rollback/pre-specialized-model-level-0` @ `f5bbf24` |
| Proposed release | **v1.69.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR |

## Request

Ship Specialized Model **Level 0** (Notion training ladder): **no fine-tuning**.
Provide a gated local baseline harness that (1) freezes a held-out evaluation
gold set, (2) scores retrieval + prompt baselines (and an optional local student
inference stub), (3) consumes permission-checked C7 training-export manifests,
and (4) records license/redaction/provenance + go/no-go evidence — without
training weights, uploading data, or auto-promoting models.

## Problem Statement

C7 can export reviewed trajectories and oversight/E2E measure Cognitive Core
surfaces, but Specialized Model work has no control-repo Level 0 baseline.
Notion requires RAG/prompt/local-student baselines **before** any LoRA. Without
Level 0, Level 1+ risks training without a held-out comparison or license gates.

## Desired Outcome

1. Gated surface (default off):
   - `./scripts/run-specialized-model.sh baseline …`
   - `northstar specialized baseline …`
   - Gate: `COMPASS_SPECIALIZED_MODEL_ENABLED=1` (or `--enable-gates`)
2. Held-out gold set under `tests/fixtures/specialized-model-gold/` (start
   ~20–40 tasks spanning state citation, triage, planning, tools, review —
   grow toward Notion’s 100–500 later)
3. Baseline report schema `specialized-model-baseline-report`:
   - retrieval score (reuse brain/e2e goldset patterns where applicable)
   - prompt-bundle / stub-student scores (hermetic fixture student OK)
   - optional compare vs a C7 `train export` manifest (`--export-id` / path)
   - `weights_trained: false`, `auto_uploaded: false`, authority flags false
4. Explicit license/redaction/provenance checklist fields on the report
5. Evidence under `.agent/evidence/specialized-model-level-0/`
6. Doctor + unit tests; CI offline (no live model download required)
7. Docs: TESTING, ADR, CHANGELOG **v1.69.0**; pointer that weights/adapters
   live **outside** this control repo

## Acceptance Criteria

- [ ] `specialized baseline` runs hermetically when gated
- [ ] Fail-closed without `COMPASS_SPECIALIZED_MODEL_ENABLED`
- [ ] Gold set fixture present; baseline report schema-validated
- [ ] `weights_trained` and `auto_uploaded` always false
- [ ] Can attach/score against a C7 export (fixture OK)
- [ ] Doctor + unit tests; evidence recorded
- [ ] Docs/ADR/CHANGELOG; PR after approval (standing order)

## Non-Goals

- Level 1+ LoRA/QLoRA / MLX training runs
- Storing model weights or adapters in this repository
- Automatic model promotion into Adaptive Intelligence routing
- Training current repository HEAD into weights as a substitute for retrieval
- Live GPU rental / cloud training jobs
- Expanding C7 export authority

## Assumptions

1. C7 `train export|review` remains the only trajectory hand-off into this path.
2. Local student inference is optional and stubbed in CI; live Ollama/MLX is
   Captain-opt-in outside CI.
3. Gold-set size for v1.69.0 is a starter set; Notion’s 100–500 is aspirational.

## Open Questions (defaults if approve as written)

1. **Student in CI:** fixture stub only → default **yes** (live local student
   documented, not required).
2. **Gold-set size for v1.69.0:** 24 fixture tasks → default **24**.
3. **Package layout:** thin `orchestrator/specialized/` in control repo for
   Level 0 only; external package deferred → default **in-repo Level 0 module**.

## Current-State Analysis

| Asset | Role |
|---|---|
| `orchestrator/train_bridge/` | C7 reviewed export manifests |
| `orchestrator/e2e/` + brain goldset | Retrieval baseline patterns |
| `orchestrator/training/from_experience.py` | Skill draft path (distinct; not weight training) |
| Notion Specialized Model page | Level 0–5 ladder + contracts |

## Proposed Architecture

```text
northstar specialized baseline
        │
        ├── require COMPASS_SPECIALIZED_MODEL_ENABLED
        ├── load gold set fixtures
        ├── score retrieval / prompt / stub-student (hermetic)
        ├── optional attach C7 export manifest
        ├── license/redaction/provenance checklist
        └── write baseline report (weights_trained=false)
```

## Workstreams

| ID | Scope |
|---|---|
| W1 | Schema + gold fixtures + scorer |
| W2 | `run-specialized-model.sh` + northstar wiring + doctor |
| W3 | Unit tests + hermetic evidence |
| W4 | Docs / ADR / CHANGELOG / weights-outside-repo note |

## Files Expected to Change

- `orchestrator/specialized/` (new)
- `orchestrator/schemas/specialized-model-baseline-report.schema.json` (new)
- `tests/fixtures/specialized-model-gold/`
- `scripts/run-specialized-model.sh`, `scripts/northstar`, `scripts/doctor.sh`
- `tests/orchestrator/test_specialized_model_level_0.py`
- `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md`
- `docs/plans/SPECIALIZED_MODEL_LEVEL_0.md`
- `.agent/evidence/specialized-model-level-0/`

## Testing Strategy

- Unit: fail-closed gate; authority/`weights_trained` locks; gold scorer
- Hermetic baseline run offline
- Regression: C7 train bridge tests still pass
- Doctor: schema + script + fail-closed

## Security Review

- Reuse C7 redaction patterns; never embed secrets in gold fixtures
- No network model download in default CI path
- Never auto-promote adapters into routing

## Rollback Plan

Tag `rollback/pre-specialized-model-level-0` @ `f5bbf24`; revert PR.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Scope into LoRA | Hard Level 0 non-goal |
| Weights accidentally committed | Explicit docs + doctor note; no weight paths in-repo |
| Gold set too large for v1 | Start at 24; grow later |

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 10 |
| Wall time | 6 hours |
| After approval | implement → validate → commit → open PR |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve specialized-model-level-0** (or revise open questions). After
approval, First Mate will branch, implement, validate, **commit, and open the PR**.
Merge remains yours.
