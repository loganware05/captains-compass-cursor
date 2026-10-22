# N1 Operational Reconciliation — Validation

| Check | Result |
|---|---|
| Unit `test_n1_status_closeout.py` | PASS (5) |
| Unit `test_m51_project_overseer.py` | PASS (15) |
| `./scripts/doctor.sh` | PASS (0 errors) |
| `status closeout` fail-closed without gate | PASS (doctor) |
| `COMPASS_STATUS_ENABLED=1 northstar status closeout` | PASS — readiness `needs_captain_action` (open completed issues await Captain close); `issues_auto_closed: false` |
| Skill count | **47** Skills with `SKILL.md`; `.cursor/skills/inodes/` is content store |
| Specialists | 12 |
| Rollback tag | `rollback/pre-n1-operational-reconciliation` @ `c7679bf` |

Artifacts: `CLOSEOUT_LEDGER.json`, `CLOSEOUT_LEDGER.md`, `CLOSEOUT_REPORT.json`.
