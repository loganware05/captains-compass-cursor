# M22 NorthStar Unattended Live Ops — Validation

**Date:** 2026-09-09  
**Branch:** `cursor/m22-northstar-unattended-ops-6044`  
**Commit:** `79962fa`  
**Plan:** `m22-m23-northstar-ops-ti-flywheel` (Captain APPROVED 2026-09-09)  
**Rollback:** `rollback/pre-m22-northstar-ops`

## Commands

```bash
./scripts/doctor.sh
# Doctor passed: 0 errors, 0 warning(s)

PYTHONPATH=. python3 -m unittest \
  tests.orchestrator.test_m22_northstar_live \
  tests.orchestrator.test_m21_northstar \
  tests.orchestrator.test_issue50_m4_bridge -v
# Ran 56 tests in ~3.1s — OK
#   M22: 29
#   M21: 22
#   #50 M4 bridge: 5

./tests/run.sh
# Results: 121 passed, 0 failed
```

## Fail-closed checks covered

- Fixture mode default; live `--approve` shortcut refused
- HMAC signature reject (401); fixture webhook 503
- Sandbox-only product allowlist (`BLOCKED_SCOPE`)
- Slack/Linear `authoritative: false`
- Wrong Cursor agent → `BLOCKED_AGENT_IDENTITY`
- Secrets redacted (`webhook_secret`, signatures, `NORTHSTAR_*` tokens)
- No live credentials in CI (`RecordingTransport` only)

## Gaps / deferred

- **Slack richer intake polish:** notify path is live-capable via transport;
  richer Slack *intake* webhook surface deferred (plan: notify after GH+Linear;
  intake polish may land with M23 if needed).
- **Sandbox refresh PR** to Compass **1.27.0** — pending after control merge/tag.
- **Release tag `v1.27.0`** — pending Captain merge.
- **M23** (TI scorecard + skill flywheel) — not started (explicitly out of scope).

## Rollback

```bash
git checkout rollback/pre-m22-northstar-ops
# or reset branch to the tag
```
