# Implementation Plan — N3 Adaptive Intelligence Validation

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `n3-adaptive-intelligence-validation` |
| Issue | *(placeholder — Captain may file)* |
| Baseline | **v1.72.0** @ `415c637` (#239 merged) |
| Branch | `cursor/n3-adaptive-intelligence-validation-673a` |
| Rollback | `rollback/pre-n3-adaptive-intelligence-validation` @ `415c637` |
| Proposed release | **v1.73.0** |
| Captain | Logan Ware |
| Created | 2026-10-22 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-10-22 |
| Notes | Explicit: “proceed with N3” after merging N2 PRs. Standing order applies. |

## Request

Connect hermetic evaluation surfaces (brain goldset, assess backtest, model-route
eval, Skill ranking / Experiences, review precision fixtures, context retrieval,
Specialized Model Level 0 baseline) into one **Adaptive Intelligence scorecard**.
Measure baseline vs evidence-informed phases, record deltas, and emit a
**Level 3 recommendation** that remains proposal-only (default: keep deferred
unless held-out training signal clearly beats retrieval).

## Desired Outcome

1. Gated `northstar adaptive scorecard` / `run-adaptive-intelligence.sh`
   (`COMPASS_ADAPTIVE_INTEL_ENABLED` or `--enable-gates`)
2. Schema-validated scorecard with seven metrics + authority locks
3. `baseline` / `with_evidence` / `compare` phases; Experiences may inform Skill
   reuse scoring only — never auto-apply weights/policies/Skills
4. Level 0 specialized rates included as training-effectiveness proxy
5. Explicit `level3_recommendation`: `defer` | `consider` with rationale
6. Evidence under `.agent/evidence/n3-adaptive-intelligence-validation/`
7. Docs/ADR/CHANGELOG **v1.73.0**; Level 3 plan stays **DEFERRED** unless
   scorecard says `consider` **and** Captain separately approves Level 3

## Acceptance Criteria

- [x] Fail-closed without adaptive gate
- [x] Scorecard covers all seven metrics (hermetic fixtures)
- [x] Compare phase records deltas; `auto_applied: false`
- [x] Level 3 recommendation field present; default path keeps Level 3 deferred
- [x] Doctor + unit tests; evidence recorded
- [x] No paid GPU; no Skill/policy auto-promotion

## Non-Goals

- Implementing Specialized Model Level 3 harness expansion
- Paid GPU jobs / weight commits / auto-promotion
- Silent self-modification of routing weights or Skills
- Claiming production specialized-model deployment

## Open Questions (defaults — approved as written)

1. Gate: `COMPASS_ADAPTIVE_INTEL_ENABLED` + `--enable-gates` → **yes**
2. Release: **v1.73.0** → **yes**
3. Level 3: keep **DEFERRED** unless stub_student clearly beats retrieval on
   held-out gold **and** Captain later approves Level 3 plan → **yes**
