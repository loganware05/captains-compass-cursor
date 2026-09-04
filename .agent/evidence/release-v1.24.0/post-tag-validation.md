# Post-tag validation — v1.24.0

| Check | Result |
|---|---|
| Release tag `v1.24.0` | Pass — https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.24.0 |
| GitHub release published | Pass |
| Automated sandbox smokes | Pass — `sandbox-smokes-automated.json` |
| Interactive smoke attestation | Pass — `sandbox-smokes-interactive.json` (item 9 fixture path; items 1–8 carry-forward) |
| Smoke evidence gate | Pass — `validate-sandbox-release-smokes.sh --version 1.24.0` |
| Private sandbox refresh | **Pending Captain** — `captain-compass-sandbox` not reachable from cloud agent (404) |
| Doctor on disposable sandbox | Pass — `/tmp/captain-compass-sandbox-v124` @ 1.24.0 |

Date: 2026-09-04
