# Post-merge closeout — post-merge-wave-continue

| Item | Value |
|---|---|
| Merge | [#275](https://github.com/loganware05/captains-compass-cursor/pull/275) @ `6ee5fb6` |
| Head before merge | `27b135e` |
| Release | **v1.87.0** |
| Issue | [#274](https://github.com/loganware05/captains-compass-cursor/issues/274) (close with this closeout) |
| Rollback | `rollback/pre-post-merge-wave-continue` @ `9e2c0d1` |
| Merged at | 2026-11-14T20:16:05Z |

## Shipped

- Skill `post-merge-wave-continue` + rule 01 / handbook / github+PR Skill cross-links
- Wave ledger schema + `northstar plan waves` / `continue-after-merge`
- ADR-109; guide `docs/guides/post-merge-wave-continue.md`
- Waves A+B (+ Wave C docs) landed in a **single** PR

## Dogfood

On merge SHA, `northstar plan continue-after-merge --plan-id post-merge-wave-continue --pr …/pull/275` verified MERGED via `gh` and advanced wave-a → next brief for wave-b (ledger semantics for multi-PR arcs; this release used one PR for all waves). Transcripts: `post-merge-continue.json`, `post-merge-waves-init.json`.

## Follow-on

None required for this plan. Optional later: T3 native merge-wake (upstream ask).
