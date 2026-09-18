# Budget — m40-filesystem-gated-context

| Field | Value |
|---|---|
| Plan | m40-filesystem-gated-context |
| Status | validating (APPROVED 2026-09-18; implementation + adversarial remediation done) |
| Soft stop | AC 1–10 + tests/evals/doctor green + sandbox evidence + PR |
| Hard stop | Never weaken fail-closed hooks, tests, or M27–M33 review locks |
| Max iterations | 40 implementation/validation cycles |
| Max failed validation cycles | 6 consecutive → Budget Stop Report |
| Scope stop | Any change outside plan "Files Expected to Change" → return to gate |
| On limit | Write `.agent/evidence/m40-filesystem-gated-context/BUDGET_STOP_REPORT.md` and stop |

## Iteration log

| When | Note |
|---|---|
| 2026-09-18 | Planning phase: startup sequence, current-state evidence analysis, capability planning artifacts (`resolve.json`, `task-graph.json`, `manifests.json`) under `.agent/plans/m40-filesystem-gated-context/`, plan authored AWAITING APPROVAL |
| 2026-09-18 | Captain approved; rollback tag `rollback/pre-m40-filesystem-gated-context` @ 125d53e; WS1–WS6 implemented with per-workstream commits |
| 2026-09-18 | WS7 sandbox validation: update.sh 1.28.0→1.40.1, npm lint/test/build green, boundary precision 1.0 (clean 0 FP / seeded 3/3) |
| 2026-09-18 | Adversarial review (bc-26d74938): H1–H6, M7–M13, L14–L19 remediated; 26 regression tests; battery re-green (125/458/43) |
