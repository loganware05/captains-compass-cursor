# Evidence — audit-p3-openui-viewer (#291)

| Field | Value |
|---|---|
| Plan | `audit-p3-openui-viewer` |
| Issue | #291 |
| Branch | `feature/291-audit-p3-openui-viewer` |
| Baseline | `257a8e7` / v1.88.0 tip |
| Rollback | `rollback/pre-audit-p3-openui-viewer` |
| Release | v1.89.0 |

## Validation

| Check | Result | Artifact |
|---|---|---|
| Unit: openui preview + control plane | pass | (unittest) |
| `./scripts/doctor.sh` | pass | `doctor.txt` |
| `./tests/run.sh` | 138 passed, 0 failed | `tests-run.txt` |

## Security notes

- Approve/reject gates unchanged (`COMPASS_CAPTAIN_APPROVE`)
- `ui serve` rejects non-localhost hosts
- Preview never auto-approves; authority locks false
