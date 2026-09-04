# Progress

## Current status

**M19 + M20 on main.** Release prep **v1.24.0** in progress.

- M19: [#111](https://github.com/loganware05/captains-compass-cursor/issues/111) / [#112](https://github.com/loganware05/captains-compass-cursor/pull/112) (merged)
- M20: [#113](https://github.com/loganware05/captains-compass-cursor/issues/113) / [#114](https://github.com/loganware05/captains-compass-cursor/pull/114) + [#115](https://github.com/loganware05/captains-compass-cursor/pull/115) (merged)
- Release branch: `chore/113-release-v1.24.0`
- Rollback: `rollback/pre-m19-skill-learning`

## Completed

- v1.5.0–v1.22.0 / M1–M18
- M19 skill learning loop
- M20 experience bridge + Captain-gated improvement apply
- Disposable sandbox install + automated release smokes for 1.24.0
- Checklist item 9 fixture path exercised

## Next

1. Merge release prep PR → tag `v1.24.0` → GitHub release
2. Captain: refresh private `captain-compass-sandbox` via `./scripts/update.sh` (agent has no access; 404)
3. Close #113 after release publish

## Blockers

Private sandbox repository not accessible from this cloud agent.
