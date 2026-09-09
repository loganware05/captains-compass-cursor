# Post-tag validation — v1.26.0

| Check | Result |
|---|---|
| Release tag `v1.26.0` | Pass — https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.26.0 |
| GitHub release published | Pass |
| Feature PR merged | Pass — [#125](https://github.com/loganware05/captains-compass-cursor/pull/125) |
| Issue #50 closed | Pass — via [#124](https://github.com/loganware05/captains-compass-cursor/pull/124) |
| Doctor + `tests/run.sh` on release commit | Pass — 121/121 |
| Automated sandbox smokes | Pass — `sandbox-smokes-automated.json` |
| Interactive smoke attestation | Pass — `sandbox-smokes-interactive.json` (item 9 + NorthStar M4 bridge fixture; items 1–8 carry-forward) |
| Smoke evidence gate | Pass — `validate-sandbox-release-smokes.sh --version 1.26.0` |
| Private sandbox refresh PR | Pass — [sandbox#42](https://github.com/loganware05/captain-compass-sandbox/pull/42) (`6aa90b5`, doctor green, 21/21) |
| Rollback | `rollback/pre-issue-50-m4-bridge` |

Date: 2026-09-09
