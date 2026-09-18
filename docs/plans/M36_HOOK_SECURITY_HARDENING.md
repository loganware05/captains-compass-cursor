# Implementation Plan — M36 / Fail-closed hook security hardening

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** (Captain directed: fix Agentic Security Review findings on PR #7) |
| Plan ID | `m36-hook-security-hardening` |
| Supersedes | — (hotfix on C2 install path; pairs with `c2-product-repo-install`) |
| Product | **NorthStar** |
| Baseline | `v1.38.0` / C2 branch `cursor/m35-c2-product-repo-install-3b10` |
| Prepared | 2026-09-16 |
| Approved | 2026-09-16 — Captain: fix the two medium hook findings on bitcoin-data-collector PR #7 |
| Linear | OVA-51 (C2) + follow-on |
| Control repo | `loganware05/captains-compass-cursor` |
| Target product | `loganware05/bitcoin-data-collector` (PR #7 refresh) |
| Proposed release | **v1.38.1** |
| Rollback tag | `rollback/pre-m36-hook-security-hardening` |
| Branch | `cursor/m36-hook-security-hardening-3b10` |
| Captain | Logan Ware |

## Acceptance criteria

1. Plan-approval hook not self-servable via Write to `IMPLEMENTATION_PLAN.md` ✅
2. Product edits require committed APPROVED plan with real approval fields ✅
3. Protected-branch denies `HEAD:main` / `push origin main` / `git -C` / checkout short-circuit ✅
4. Hermetic unit + `tests/run.sh` / eval coverage ✅
5. Control PR ready; product refresh instructions for PR #7 ✅
6. Agentic security → NorthStar Code Reviewer integration plan drafted (separate) ✅

## Approval gate

**APPROVED** 2026-09-16 — Captain directed remediations from Cursor Agentic Security Review on PR #7.
