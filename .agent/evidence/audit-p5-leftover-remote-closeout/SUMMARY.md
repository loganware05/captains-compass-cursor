# Evidence — audit-p5-leftover-remote-closeout (#297)

| Field | Value |
|---|---|
| Plan | `audit-p5-leftover-remote-closeout` |
| Issue | #297 |
| Baseline | `9b65cd9` / v1.89.1 tip |
| Rollback | `rollback/pre-audit-p5-leftover-remote-closeout` |
| Release | v1.89.2 |

## Counts

| Metric | Value |
|---|---|
| Heads before | 5 |
| Deleted | 4 |
| Heads after | 1 (`main` only) |

## Safety

`git cherry` vs `origin/main` showed equivalent patches on main for all unique tip commits (`dossier.md`).
