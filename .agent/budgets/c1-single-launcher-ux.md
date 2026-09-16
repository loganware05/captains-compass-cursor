# Budget — c1-single-launcher-ux

| Field | Value |
|---|---|
| Plan | c1-single-launcher-ux |
| Status | active (soft stop met; awaiting merge) |
| Started | 2026-09-16 |
| Soft stop | AC met + smoke/doctor + evidence + PR |
| Hard stop | No control-script copy; no C2 product install; Linear never approves |

## Locks

1. Captain plan gate before product implementation — **satisfied**
2. Topology-free `northstar` launcher remains canonical
3. Docs/help only — full product install is C2
4. Hermetic default path
5. Skill slug `code-reviewer` unchanged

## Iteration log

| When | Note |
|---|---|
| 2026-09-16 | Plan drafted on M33 closeout PR; awaiting approval |
| 2026-09-16 | Captain approved; rollback tag created; implementation on `cursor/m34-c1-single-launcher-ux-3b10` |
| 2026-09-16 | Help + INDEX + install boundary + doctor/tests green |
