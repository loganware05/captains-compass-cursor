# Validation — openui-control-plane

| Check | Result |
|---|---|
| Unit `test_openui_control_plane` (10) | PASS |
| `orchestrator/ui` npm test | PASS |
| `./scripts/doctor.sh` | PASS (0 errors) |
| `./tests/run.sh` | PASS (125 passed, 0 failed) |
| Approve without Captain env | denied (exit 1) |
| Emit without Open UI gate | fail-closed (exit 2) |
| Emit plan/tower/scorecard/closeout | OpenUI Lang validates |
| Browser preview screenshot | `preview.png` |
| Rollback tag | `rollback/pre-openui-control-plane` @ 6432c23 |
