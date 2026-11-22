# Implementation Plan — Audit P4 Remote Hygiene

- Status: **APPROVED** (implementation in progress)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `audit-p4-remote-hygiene` |
| Issue | [#294](https://github.com/loganware05/captains-compass-cursor/issues/294) |
| PR | [#295](https://github.com/loganware05/captains-compass-cursor/pull/295) |
| Baseline | `origin/main` @ `28bd0c2` / **v1.89.0** tip after #293 |
| Branch | `docs/294-audit-p4-remote-hygiene` |
| Rollback | `rollback/pre-audit-p4-remote-hygiene` @ `28bd0c2` |
| Proposed release | **v1.89.1** |
| Created | 2026-11-22 |
| Approved by | Logan Ware (Captain) — 2026-11-22 |

Budget: `.agent/budgets/audit-p4-remote-hygiene.md`  
Durable copy: `docs/plans/AUDIT_P4_REMOTE_HYGIENE.md`  
Evidence: `.agent/evidence/audit-p4-remote-hygiene/`

## Approval decisions

| Q | Decision |
|---|---|
| Q1 Hygiene-only | **yes** |
| Q2 Dry-run merged allowlist | **yes** |
| Q3 Enable auto-delete | **yes** |
| Q4 Prefer XRV/Bend | **no** |

## Delivered (this branch)

1. Dry-run allowlist: 199 merged remotes; 5 skipped (main + 4 unmerged).
2. Deleted 199 remote heads (204 → 5).
3. Enabled `delete_branch_on_merge=true`.
4. Archived obsolete P1/P2 awaiting stubs under `docs/plans/archive/`.

## Out of scope (deferred)

T3 live · specialized · B4 · XRV ops-verified · Bend #278 · the 4 leftover unmerged branches

## Acceptance criteria

- [x] Dry-run allowlist in evidence before deletes
- [x] Remote head count reduced; deleted refs listed
- [x] `delete_branch_on_merge` enabled
- [x] P1/P2 awaiting stubs archived
- [x] doctor + tests green; PR cited ([#295](https://github.com/loganware05/captains-compass-cursor/pull/295))
