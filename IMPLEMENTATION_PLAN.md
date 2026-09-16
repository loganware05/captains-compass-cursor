# Implementation Plan — M36 / Fail-closed hook security hardening

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED — IMPLEMENTING** (Captain directed: fix Agentic Security Review findings on PR #7) |
| Plan ID | `m36-hook-security-hardening` |
| Supersedes | — (hotfix after C2 install; pairs with closed `c2-product-repo-install` / v1.38.0) |
| Product | **NorthStar** |
| Baseline | **v1.38.0** tagged @ `c8c1345` (M35 / C2 merged) |
| Prepared | 2026-09-16 |
| Approved | 2026-09-16 — Captain: fix the two medium hook findings on bitcoin-data-collector PR #7 |
| Linear | OVA-51 (C2) + follow-on |
| Control repo | `loganware05/captains-compass-cursor` |
| Target product | `loganware05/bitcoin-data-collector` (hooks refresh after #7 merge) |
| Proposed release | **v1.38.1** |
| Rollback tag | `rollback/pre-m36-hook-security-hardening` |
| Branch | `cursor/m36-hook-security-hardening-5182` (rebase onto `main`; was `…-3b10`) |
| Control PR | [#167](https://github.com/loganware05/captains-compass-cursor/pull/167) |
| Captain | Logan Ware |

## Acceptance criteria

1. Plan-approval hook not self-servable via Write to `IMPLEMENTATION_PLAN.md` ✅
2. Product edits require committed APPROVED plan with real approval fields ✅
3. Protected-branch denies `HEAD:main` / `push origin main` / `git -C` / checkout short-circuit ✅
4. Hermetic unit + `tests/run.sh` / eval coverage ✅
5. Control PR retargeted to `main` after C2 merge (branch conflict resolved) ✅
6. Product hooks refreshed on bitcoin-data-collector (post-#7 merge) ⬜
7. Agentic security → NorthStar Code Reviewer integration plan drafted (separate) ✅

## Residual

1. Merge control PR #167 → tag **v1.38.1**
2. Ship product hooks refresh PR (APPLY_TO_PR7 against `cursor/kalshi-live-decision-system`)
3. Captain approve `docs/plans/AGENTIC_SECURITY_REVIEW_INTEGRATION.md` for M37

## Approval gate

**APPROVED** 2026-09-16 — Captain directed remediations from Cursor Agentic Security Review on PR #7.
