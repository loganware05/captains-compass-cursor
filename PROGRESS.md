# Progress

## Current status

**M19 + M20 CLOSED** — shipped as **v1.24.0**.

- Release: [v1.24.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.24.0)
- Feature PRs: [#112](https://github.com/loganware05/captains-compass-cursor/pull/112), [#115](https://github.com/loganware05/captains-compass-cursor/pull/115)
- Release prep: [#116](https://github.com/loganware05/captains-compass-cursor/pull/116)
- Closeout: [#117](https://github.com/loganware05/captains-compass-cursor/pull/117) (merged)
- Issues: [#111](https://github.com/loganware05/captains-compass-cursor/issues/111), [#113](https://github.com/loganware05/captains-compass-cursor/issues/113) (closed)
- Rollback: `rollback/pre-m19-skill-learning`

**M21:** Captain is drafting a separate M21 plan — path options A–E in this repo are **parked / disregard**.

## Completed

- v1.5.0–v1.24.0 / M1–M20
- M19 skill learning loop (#111 / #112)
- M20 experience bridge + Captain-gated Skill improvement apply (#113 / #115)
- v1.24.0 tag + GitHub release + closeout #117

## Next

1. **Sandbox refresh to 1.24.0** — local update+doctor+commit ready (`chore/refresh-compass-1.24.0` @ `a9a7f0c`); **push still 403** for `cursor[bot]`. Need Cursor GitHub App write on `captain-compass-sandbox` (installation currently control-repo only) **or** Captain applies patch `.agent/evidence/sandbox-refresh-1.24.0/`.
2. Land Captain’s forthcoming M21 plan (separate from parked A–E options).
3. Hygiene: close stale shipped issue [#50](https://github.com/loganware05/captains-compass-cursor/issues/50) (M4 / v1.8.0 already shipped).

## Blockers

`git push` to https://github.com/loganware05/captain-compass-sandbox.git returns `Permission denied to cursor[bot]`. Cloud Agent token is a GitHub App installation token; App installation repos = `captains-compass-cursor` only. Environment repos list also lacks the sandbox.
