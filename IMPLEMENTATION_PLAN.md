# Implementation Plan — Audit P0 Governance & Hygiene

- Status: **VALIDATING**

## Metadata

| Field | Value |
|---|---|
| Status | **VALIDATING** |
| Plan ID | `audit-p0-governance-hygiene` |
| Issue | [#280](https://github.com/loganware05/captains-compass-cursor/issues/280) |
| Baseline | `origin/main` @ `38d3563` (v1.87.0 tip after #279) |
| Branch | `feature/280-audit-p0-governance-hygiene` from `main` |
| Rollback | `rollback/pre-audit-p0-governance-hygiene` @ `38d3563` |
| Proposed release | **v1.87.1** (patch) |
| Created | 2026-11-21 |
| Approved by | Logan Ware (Captain) — chat "Approve" |
| Approval date | 2026-11-21 |
| Approved revision | Q1=yes replace active plan; Q2=keep #278 open for Bend follow-ups (default); Q3=no P1 in same PR (default); Q4=HTML archive optional later (default) |
| Source audit | Cloud agent `bc-22bbacc4-5283-4fa1-a382-29baec9fff57`; canvas evidence under `.agent/evidence/northstar-full-audit-2026-11-20/` |
| Worktree | `/Users/loganware/Documents/Personal/Code/captains-compass-cursor-audit-p0` |

Budget: `.agent/budgets/audit-p0-governance-hygiene.md`  
Durable copy: `docs/plans/AUDIT_P0_GOVERNANCE_HYGIENE.md`  
Capability artifacts: `.agent/plans/audit-p0-governance-hygiene/`

**Supersedes as active gate:** `bend-policy-proof-spike` (PR #279 merged). Durable text: `docs/plans/BEND_POLICY_PROOF_SPIKE.md`.

## Scope (P0)

1. Finding 001 — `ensure_policy_for_instruction` always starts at `candidate`.
2. Test isolation — N3/specialized dry-run must not dirty tracked fixtures.
3. Post-merge closeout — PROGRESS/#247/#278 dispositions; keep #278 open.

## Acceptance criteria

- [x] New policies always begin at `candidate`; regression tests cover elevated instruction states.
- [x] Targeted/full tests leave tracked fixtures clean.
- [x] `./scripts/doctor.sh` passes (0 errors).
- [x] Memory docs + issue dispositions recorded (#247 closed; #278 kept open).
- [x] Evidence under `.agent/evidence/audit-p0-governance-hygiene/`.
- [ ] PR opened from feature branch off `main`.
