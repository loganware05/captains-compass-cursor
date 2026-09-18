# Budget — m40-filesystem-gated-context

| Field | Value |
|---|---|
| Plan | m40-filesystem-gated-context |
| Status | planning (AWAITING APPROVAL) |
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
