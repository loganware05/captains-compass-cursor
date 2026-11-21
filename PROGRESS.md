# Progress

## Current status

**IN PROGRESS:** [#280](https://github.com/loganware05/captains-compass-cursor/issues/280) /
`audit-p0-governance-hygiene` on `feature/280-audit-p0-governance-hygiene` → **v1.87.1**.

| Item | Value |
|---|---|
| Baseline | **v1.87.0** @ `38d3563` |
| Active plan | `audit-p0-governance-hygiene` **IN PROGRESS** |
| Issue | [#280](https://github.com/loganware05/captains-compass-cursor/issues/280) |
| Rollback | `rollback/pre-audit-p0-governance-hygiene` @ `38d3563` |
| Worktree | `captains-compass-cursor-audit-p0` |

### Prior closeout

- Bend policy-lifecycle proof spike **merged** [#279](https://github.com/loganware05/captains-compass-cursor/pull/279) for [#278](https://github.com/loganware05/captains-compass-cursor/issues/278) → **v1.87.0** tip `38d3563`. Issue **#278 stays open** for Bend follow-ups (entry-state law, P4/P5 history, Lean pin, ADR-110 go/no-go). Finding 001 production bypass fixed in #280.
- Conversation trajectory ingest **shipped** via [#248](https://github.com/loganware05/captains-compass-cursor/pull/248) (v1.77.0); Issue #247 closed as completed.
- Post-merge wave continue **v1.87.0** (#275 / #274)
- XRV W3 **v1.85.0** (#267); Superpowers + C2 **v1.86.0** (#273)

## Standing order

Approve ⇒ implement → validate → commit → open PR. Merge remains Captain-only.

## Validation (local)

- Finding 001 + N3 + specialized dry-run targeted tests: pass
- Formal KnownGapTests (`bypass_observed=False`): pass
- `unittest discover` orchestrator: **942 OK** (11 skipped)
- Tracked fixture hygiene after tests: clean
- `./scripts/doctor.sh`: **0 errors**, 1 warning (skill inode carry-over — P1 backlog)
- Evidence: `.agent/evidence/audit-p0-governance-hygiene/`

## Blockers

None.
