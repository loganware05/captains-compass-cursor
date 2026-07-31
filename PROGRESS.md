# Progress

## Current status

**V1.2.0 released.** Tag/release
[`v1.2.0`](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.2.0)
points at `56c1227` (PR #27). Sandbox refresh PR is open; P1 plan is next
(awaiting approval).

## Completed

- Full Skill set through iOS (v0.7) and stable polish (v1.0)
- Seven hooks + GitHub Stage 1
- `update.sh` / `uninstall.sh`, UPGRADING, RELEASE_CHECKLIST, Postgres MCP Stage 6
- Template repository + topics on GitHub
- Releases through [v1.0.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.0.0)
- Sandbox approval-gate exercise (contact form) and upgrade path through 1.0.0
- `docs/PRODUCT_ONBOARDING.md` + memory refresh (#14 / PR #15)
- Sandbox failure tests 1–6 — #16 / PR #17
- Agent install/activation prompts — #18
- V1.1.0 Micky-inspired Skills — #19 / PR #20
- Latest/pinned forward update documentation — #21 / PR #22
- Repaired v1.1.0 tag/release; preserved rollback tag — #23
- Release checklist hardening/evidence — #23 / PR #24
- Sandbox v1.1.0 workflow refresh — sandbox #5 / PR #6
- P0 fail-closed hooks + autonomy budgets + control CI — #26 / PR #27 / **v1.2.0**

## In progress

- Sandbox v1.2.0 refresh — [sandbox #7](https://github.com/loganware05/captain-compass-sandbox/issues/7) / [PR #8](https://github.com/loganware05/captain-compass-sandbox/pull/8)
- P1 plan draft — [`docs/plans/P1_AWAITING_APPROVAL.md`](docs/plans/P1_AWAITING_APPROVAL.md)

## Next

- Captain merges sandbox PR #8
- Approve P1 plan (then promote to root `IMPLEMENTATION_PLAN.md`)
- Then P2 (evals, harness GC, session ledger, structural tests, supply-chain)

## Blockers

None.

## Known follow-up (non-blocking)

Soft Cursor shell hooks (`pre-commit-formatting`, `pre-push-tests`) can deny in
the agent runner even when `npm run lint` / `npm test` pass locally; `COMPASS_SKIP_*`
env vars are not reliably visible to Cursor’s hook process. Consider detecting
`git -C` / improving skip signaling in a later plan.
