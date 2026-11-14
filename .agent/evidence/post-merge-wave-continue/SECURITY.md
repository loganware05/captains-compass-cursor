# Security review — post-merge-wave-continue (#274)

## Surface

- New Skill (procedure only) + CLI that shells to `gh pr view --json …`
- Wave ledger JSON under `.agent/plans/<plan-id>/wave-ledger.json`

## Findings

| ID | Severity | Finding | Mitigation |
|---|---|---|---|
| S1 | Low | Untrusted PR titles/bodies never parsed as instructions | CLI uses state/mergedAt/mergeCommit only |
| S2 | Low | Webhook path (optional Wave C) could spoof merge | Documented: re-verify with `gh` after signal; poll is default |
| S3 | Info | `gh` token stays local | No token logging; errors print stderr text only |

## Authority

- Never auto-merges
- Never writes `APPROVED` into `IMPLEMENTATION_PLAN.md`
- Schema locks: `approved_for_execution`, `authority_mutation`, `auto_merge` const false

## Verdict

PASS for v1.87.0 ship — no blocking security defects.
