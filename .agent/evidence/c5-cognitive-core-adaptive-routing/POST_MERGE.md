# Post-merge smoke — C5 @ main

| Field | Value |
|---|---|
| Merge | [#213](https://github.com/loganware05/captains-compass-cursor/pull/213) |
| Commit | `56ac9de` |
| VERSION | 1.64.0 |
| Date | 2026-10-19 |

## Checks on `main` after merge

| Check | Result |
|---|---|
| `./scripts/doctor.sh` | PASS |
| `test_c5_cognitive_core_adaptive_routing.py` | PASS (10) |
| `model route` smoke | PASS — `local`, version 1.64.0, `auto_switched: false` |
| `model evaluate` smoke | PASS — recommended `local`, authority flags false |
| C3 `assess` regression | PASS — version 1.64.0 |

## Closeout

- Plan mirror marked **COMPLETE**
- PROGRESS updated; C6 plan drafted **AWAITING APPROVAL** (#214)
- GitHub issue #211 already closed by merge
- ExecutionRun / Experience recorded locally (not committed)
- GitHub release tag `v1.64.0` not created this closeout (remote release tags lag; Captain may tag via `docs/RELEASE_CHECKLIST.md` if desired)
