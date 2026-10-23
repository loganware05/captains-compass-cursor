> **COMPLETE** (2026-10-22) — Plan ID `n3-adaptive-intelligence-validation`.
> Baseline: **v1.72.0** @ `415c637` / [#239](https://github.com/loganware05/captains-compass-cursor/pull/239).
> Release: **v1.73.0**.
> Evidence: `.agent/evidence/n3-adaptive-intelligence-validation/`.
> Rollback: `rollback/pre-n3-adaptive-intelligence-validation` @ `415c637`.

# N3 — Adaptive Intelligence Validation

## One-line summary

Hermetic Adaptive Intelligence scorecard composing Cognitive Core, Behavior
Loop, and Specialized Model Level 0 surfaces; compare phase recommends keeping
Level 3 **DEFERRED**.

## Operator note

```bash
./scripts/northstar adaptive scorecard --phase compare --repo . --enable-gates
# or:
COMPASS_ADAPTIVE_INTEL_ENABLED=1 COMPASS_BRAIN_ENABLED=1 \
  COMPASS_ASSESS_ENABLED=1 COMPASS_ROUTE_ENABLED=1 \
  ./scripts/run-adaptive-intelligence.sh scorecard --phase compare --repo-root .
```

## Scorecard metrics

| Metric | Definition |
|---|---|
| Project-state accuracy | Grounded claims / checked claims |
| Difficulty calibration | Assess backtest pass rate |
| Routing effectiveness | Model-route composite (inverse) |
| Skill reuse | Held-out objective Skill hit-rate (+ Experiences in with_evidence) |
| Review precision | Accepted verified findings / decided findings |
| Context efficiency | Evidence-linked retrieval density |
| Training effectiveness | Level 0 stub_student vs retrieval rates |

Authority locks: `auto_applied`, `authority_mutation`, `approved_for_execution`
are always **false**.

## Level 3 recommendation

Hermetic compare: `level3_recommendation=defer` (stub_student_rate equals
retrieval_rate). Specialized Model Level 3 stays **DEFERRED** until Captain
separately approves a Level 3 plan.

## Non-goals honored

No paid GPU; no Skill/policy auto-promotion; no silent self-modification.
