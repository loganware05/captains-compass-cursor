# Progress

## Current status

**M19 + M20 CLOSED** — shipped as **v1.24.0**.

- Release: [v1.24.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.24.0)
- Feature PRs: [#112](https://github.com/loganware05/captains-compass-cursor/pull/112), [#115](https://github.com/loganware05/captains-compass-cursor/pull/115)
- Release prep: [#116](https://github.com/loganware05/captains-compass-cursor/pull/116)
- Closeout: [#117](https://github.com/loganware05/captains-compass-cursor/pull/117) (merged)
- Issues: [#111](https://github.com/loganware05/captains-compass-cursor/issues/111), [#113](https://github.com/loganware05/captains-compass-cursor/issues/113) (closed)
- Rollback: `rollback/pre-m19-skill-learning`

**Next plan:** `m21-roadmap-options` — **AWAITING APPROVAL** (path selection).

## Completed

- v1.5.0–v1.24.0 / M1–M20
- M19 skill learning loop (#111 / #112)
- M20 experience bridge + Captain-gated Skill improvement apply (#113 / #115)
- v1.24.0 tag + GitHub release + closeout #117

## Next

1. **Sandbox refresh to 1.24.0** — local update+doctor+commit done (`chore/refresh-compass-1.24.0` @ `344c2b2`); **push still 403** for `cursor[bot]`. Captain: grant Cursor GitHub App **write** on `captain-compass-sandbox` (not just public), **or** apply patch `.agent/evidence/sandbox-refresh-1.24.0/` and open the PR.
2. **Captain picks M21 path** (see `IMPLEMENTATION_PLAN.md` options A–E).
3. Hygiene: close stale shipped issue [#50](https://github.com/loganware05/captains-compass-cursor/issues/50) (M4 / v1.8.0 already shipped).

## Blockers

Sandbox repo is readable (public) but **not** in the Cursor GitHub App installation with write — `git push` returns `Permission denied to cursor[bot]`. Need App write access (or Captain-local push of ready commit/patch).
