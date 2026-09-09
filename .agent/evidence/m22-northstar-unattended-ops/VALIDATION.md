# M22 NorthStar Unattended Live Ops — Validation

**Date:** 2026-09-09  
**Branch:** `cursor/m22-northstar-unattended-ops-6044`  
**Commit:** `8690f6f` (security hardening on `79962fa`)  
**Plan:** `m22-m23-northstar-ops-ti-flywheel` (Captain APPROVED 2026-09-09)  
**Rollback:** `rollback/pre-m22-northstar-ops`
**PR:** https://github.com/loganware05/captains-compass-cursor/pull/129

## Commands

```bash
./scripts/doctor.sh
# Doctor passed: 0 errors, 0 warning(s)

PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m22_northstar_live -v
# Ran 31 tests — OK
#   (includes empty-digest + fixture-captain allowlist regressions)

./tests/run.sh
# Results: 121 passed, 0 failed
```

## Fail-closed checks covered

- Fixture mode default; live `--approve` shortcut refused
- HMAC signature reject (401); fixture webhook 503
- Sandbox-only product allowlist (`BLOCKED_SCOPE`)
- Slack/Linear `authoritative: false`
- Live approval requires 64-hex `plan_digest` (empty digest → `BLOCKED_APPROVAL`)
- Fixture `captain-github` not trusted in live mode unless `NORTHSTAR_CAPTAIN_GITHUB_IDS` allowlists it
- Live ack posts to `/repos/{repo}/issues/{n}/comments`
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
