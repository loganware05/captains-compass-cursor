# N3 Adaptive Intelligence Validation — Evidence Matrix

| Step | Result | Artifact |
|---|---|---|
| Gate fail-closed | PASS exit 2 | unit `test_cli_fail_closed` + doctor |
| Schema + authority locks | PASS | `adaptive-intelligence-scorecard.schema.json` |
| Phase baseline | PASS | `LATEST_baseline.json` |
| Phase with_evidence | PASS (Experiences inform skill_reuse only) | `LATEST_with_evidence.json` |
| Phase compare | PASS deltas; `auto_applied: false` | `LATEST_compare.json` |
| Seven metrics present | PASS | compare `metrics` |
| Level 3 recommendation | **defer** | compare `level3_recommendation` |
| Doctor adaptive checks | PASS | doctor after patch |
| Unit tests | PASS | `test_n3_adaptive_intelligence.py` |

## Level 3 rationale (hermetic)

`stub_student_rate=1.000` vs `retrieval_rate=1.000` (delta=0.000) → keep
`specialized-model-level-3` **DEFERRED**.

## Non-goals honored

No paid GPU; no GitHub issue auto-close; no Skill/policy auto-promotion;
no authority mutation.
