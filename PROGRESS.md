# Progress

## Current status

**Release: v1.38.1** — M36 hook security hardening (C2 product PR #7 remediation).
**v1.38.0** tagged 2026-09-17 @ `c8c1345` after #166 + bitcoin-data-collector #7 merged.

| Item | Value |
|---|---|
| Tagged | **v1.38.0** (M35 / C2) |
| In flight | **v1.38.1** / M36 — PR [#167](https://github.com/loganware05/captains-compass-cursor/pull/167) rebased onto `main` |
| Branch | `cursor/m36-hook-security-hardening-5182` |
| Product follow-up | [bitcoin-data-collector#8](https://github.com/loganware05/bitcoin-data-collector/pull/8) hooks refresh (APPLY_TO_PR7) |
| Next plan | `docs/plans/AGENTIC_SECURITY_REVIEW_INTEGRATION.md` **AWAITING APPROVAL** |
| Rollback | `rollback/pre-m36-hook-security-hardening` |

## In flight

- Merge control M36 PR [#167](https://github.com/loganware05/captains-compass-cursor/pull/167) (rebased onto `main`; MERGEABLE) → tag **v1.38.1**
- Merge product hooks-refresh PR [bitcoin-data-collector#8](https://github.com/loganware05/bitcoin-data-collector/pull/8)
- Await Captain approval of agentic-security-review-integration (M37)

## Completed

- **M35 / C2** merged + tagged **v1.38.0** (control #166, product #7)
- **M34 / C1** → v1.37.0
- **M33 / B5** → v1.36.0 — Track B complete

## Blockers

None for M36 merge path after rebase. M37 awaits Captain plan approval.
