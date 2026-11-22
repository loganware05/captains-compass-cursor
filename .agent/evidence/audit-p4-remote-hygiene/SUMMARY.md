# Evidence — audit-p4-remote-hygiene (#294)

| Field | Value |
|---|---|
| Plan | `audit-p4-remote-hygiene` |
| Issue | #294 |
| Baseline | `28bd0c2` / v1.89.0 tip |
| Rollback | `rollback/pre-audit-p4-remote-hygiene` |
| Release | v1.89.1 |

## Counts

| Metric | Value |
|---|---|
| Heads before | 204 |
| Allowlisted (merged) | 199 |
| Deleted | 199 |
| Heads after | 5 (`main` + 4 unmerged leftovers) |
| `delete_branch_on_merge` | **true** |

## Leftover unmerged (not deleted)

- `cursor/m36-hook-security-hardening-3b10`
- `feature/111-m19-skill-learning-loop`
- `feature/113-m20-experience-bridge`
- `feature/35-m1-capability-aware-planning`

## Artifacts

- `heads-before.txt` / `heads-after.txt`
- `allowlist-dry-run.txt` / `skip-dry-run.txt`
- `deleted.txt`
- `delete-branch-on-merge.txt`
