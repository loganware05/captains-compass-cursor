# Evidence — audit-p1-doctor-ui-ci (#284)

## Changes

1. `doctor.sh` buffers `northstar help` to a temp file before grepping.
2. Skills discovered via `find .cursor/skills/*/SKILL.md` (skip `inodes/`).
3. Skill inode carry-over Captain-approved for `github-integration`, `pull-request-preparation`.
4. CI job `openui-ui` (Node 22): `npm ci` + typecheck + test; added `@types/node` for typecheck.

## Validation

| Check | Result |
|---|---|
| Help buffer stress (50x local / 20x in tests/run.sh) | pass |
| `./scripts/doctor.sh` | 0 errors, 0 warnings |
| `orchestrator/ui` typecheck + test | pass |
| `./tests/run.sh` | see `tests-run.txt` |

## Rollback

`rollback/pre-audit-p1-doctor-ui-ci` @ `266d9e2`
