# Post-tag validation — v1.25.0

| Check | Result |
|---|---|
| Release tag `v1.25.0` | Pass — https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.25.0 |
| GitHub release published | Pass |
| Feature PR merged | Pass — [#121](https://github.com/loganware05/captains-compass-cursor/pull/121) |
| Doctor + `tests/run.sh` on release commit | Pass — 121/121 |
| Automated sandbox smokes | Pass — `sandbox-smokes-automated.json` |
| Interactive smoke attestation | Pass — `sandbox-smokes-interactive.json` (item 9 + NorthStar routine fixture; items 1–8 carry-forward) |
| Smoke evidence gate | Pass — `validate-sandbox-release-smokes.sh --version 1.25.0` |
| Private sandbox refresh PR | Pass — [sandbox#41](https://github.com/loganware05/captain-compass-sandbox/pull/41) merged (`36ff5d2`, doctor green, 21/21) |
| Rollback | `rollback/pre-m21-northstar` (`13b5879`) |

Date: 2026-09-08
