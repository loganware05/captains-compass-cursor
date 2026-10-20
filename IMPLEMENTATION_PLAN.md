# Implementation Plan — E2E Cognitive Core Evaluation

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `e2e-cognitive-core-evaluation` |
| Issue | [#222](https://github.com/loganware05/captains-compass-cursor/issues/222) |
| Notion | [Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.66.1** @ `96a8de3` (#221 merged) |
| Proposed branch | `cursor/222-e2e-cognitive-core-evaluation-3ec1` |
| Proposed rollback | `rollback/pre-e2e-cognitive-core-evaluation` @ `96a8de3` |
| Proposed release | **v1.67.0** |
| Captain | Logan Ware |
| Created | 2026-10-20 |

## Approval record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR |

## Request

Ship a **bounded end-to-end Cognitive Core evaluation** after C1–C7:
hermetic harness that exercises `brain` → `assess` → `cycle` → `model` → `rea` →
`train` under existing feature gates, records measurable baselines, and optionally
runs against `captain-compass-sandbox` after a Compass refresh. No new execution
authority.

## Problem Statement

C1–C7 are implemented and feature-gated in isolation, but the Oct 20 repository
state PDF notes that interface existence does not prove cross-surface reliability.
Operators need one evidence-backed run that measures retrieval relevance,
difficulty-fit calibration, routing quality, cycle reliability, REA packet
correctness, and train-export permission/redaction — without live spend or
weight promotion.

## Desired Outcome

1. Hermetic CLI/script: `./scripts/run-cognitive-core-e2e.sh` (or `northstar
   cognitive e2e`) that:
   - Requires explicit env gates (reuse `COMPASS_*_ENABLED`; fail-closed when unset)
   - Runs C1 sync/status → C2 context/ask (goldset scorer) → C3 assess → C4
     cycle begin/checkpoint/close (fixture) → C5 model route/evaluate → C6 REA
     fixture investigate → C7 train export+review (permission checklist)
   - Emits a schema-validated report under
     `.agent/evidence/e2e-cognitive-core-evaluation/`
2. Baselines recorded (targets aspirational, not hard CI gates for v1.67.0):
   - Brain goldset evidence-link accuracy (existing harness)
   - Assess backtest calibration summary (existing fixtures)
   - Route eval fixture score
   - Cycle idempotency / authority flags always false
   - REA claim_kind separation (observed vs hypothesis)
   - Train export: redaction + permission bits + `auto_uploaded: false`
3. Optional sandbox mode: refresh sandbox Compass to 1.66.1+, doctor, then run
   the same harness against the sandbox path (control scripts still from this
   repo).
4. Doctor knows the new script/schema; unit tests for report assembly; CI stays
   offline-friendly.
5. TESTING / handbook / CHANGELOG / ADR updated.

## Acceptance Criteria

- [ ] Hermetic e2e harness runs green offline with fixture embeddings / stub
      adapters
- [ ] Report schema validates; authority flags always false
- [ ] Baselines written to evidence folder with machine-readable JSON + short MD
- [ ] Fail-closed without required `COMPASS_*_ENABLED` flags
- [ ] Optional sandbox mode documented; not required for CI
- [ ] Doctor + unit tests; no live network required in default mode
- [ ] Docs/ADR/CHANGELOG; PR opened after approval (standing order)

## Non-Goals

- Persistent post-merge Overseer automation (PDF step 3)
- Specialized Model Level 0–1 fine-tuning (PDF step 4)
- HTTP `/v1/*` Cognitive Core server
- Requiring live Kimi / live REA / live embeddings for CI
- Expanding approval or merge authority

## Assumptions

1. Existing per-milestone unit tests and fixtures remain the building blocks.
2. ≥90% brain goldset accuracy remains aspirational; v1.67.0 records measured
   baseline.
3. Sandbox refresh may be a separate chore PR on `captain-compass-sandbox`.

## Open Questions (defaults if approve as written)

1. **Surface:** thin `run-cognitive-core-e2e.sh` only vs also `northstar
   cognitive e2e` → default **both** (script + northstar alias).
2. **Sandbox in same PR:** hermetic-only for v1.67.0; sandbox evidence as
   follow-up commit/PR if refresh lags → default **hermetic required; sandbox
   optional evidence**.
3. **CI gate:** warn-only baseline thresholds in v1.67.0 → default **yes**
   (record, do not fail CI on aspirational %).

## Current-State Analysis

| Asset | Role |
|---|---|
| `orchestrator/cognitive/`, `assess/`, `cycle/`, `route/`, `rea/`, `train_bridge/` | Per-milestone services |
| `tests/fixtures/brain-goldset`, `assess-backtest`, `model-route-eval`, `rea-evidence` | Hermetic inputs |
| `tests/orchestrator/test_c{1-7}_*.py` | Unit coverage to compose |
| `orchestrator/release/sandbox_smokes.py` | Pattern for catalogued smokes (extend carefully) |
| `captain-compass-sandbox` | Optional product-repo target |

## Proposed Architecture

```text
run-cognitive-core-e2e.sh
        │
        ├── require COMPASS_* gates (or --require-gates that sets hermetic fixtures)
        ├── C1 brain sync/status
        ├── C2 brain context + goldset score
        ├── C3 assess project (fixture objective)
        ├── C4 cycle begin → checkpoint → close
        ├── C5 model route + evaluate
        ├── C6 rea investigate (fixture)
        ├── C7 train export + review
        └── write e2e-cognitive-core-report.json (+ SUMMARY.md)
```

## Workstreams

| ID | Scope |
|---|---|
| W1 | Report schema + orchestrator e2e runner composing existing CLIs |
| W2 | `scripts/run-cognitive-core-e2e.sh` + `northstar` wiring + doctor |
| W3 | Unit tests + hermetic evidence baselines |
| W4 | Docs / ADR / CHANGELOG / optional sandbox notes |

## Files Expected to Change

- `orchestrator/` e2e module (new, thin composer)
- `orchestrator/schemas/e2e-cognitive-core-report.schema.json` (new)
- `scripts/run-cognitive-core-e2e.sh`, `scripts/northstar`, `scripts/doctor.sh`
- `tests/orchestrator/test_e2e_cognitive_core_evaluation.py`
- `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md`, handbook
- `docs/plans/E2E_COGNITIVE_CORE_EVALUATION.md`
- `.agent/evidence/e2e-cognitive-core-evaluation/`

## Testing Strategy

- Unit: report assembly; fail-closed gates; authority flags
- Hermetic e2e: full C1–C7 path offline
- Regression: existing `test_c{1-7}_*` still pass
- Doctor: schema + script presence

## Security Review

- No secrets in evidence (reuse redaction helpers from train bridge)
- Default mode offline; sandbox mode still local scripts only
- Never set `approved_for_execution` / `authority_mutation` / `auto_uploaded` true

## Rollback Plan

Tag `rollback/pre-e2e-cognitive-core-evaluation` @ `96a8de3`; revert PR;
remove e2e script from doctor expectations.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Flaky sandbox path | Hermetic required; sandbox optional |
| Scope creep into oversight/training | Hard non-goals |
| Aspirational metrics fail CI | Warn-only thresholds in v1.67.0 |

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 10 |
| Wall time | 6 hours |
| After approval | implement → validate → commit → open PR |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve e2e-cognitive-core-evaluation** (or revise open questions). After
approval, First Mate will branch, implement, validate, **commit, and open the PR**.
Merge remains yours.
