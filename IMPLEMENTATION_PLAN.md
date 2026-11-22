# Implementation Plan — Audit P2 Sentry Polish & COMPASS Profiles v0

- Status: **APPROVED** (implementation in progress)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `audit-p2-sentry-profiles` |
| Issue | [#288](https://github.com/loganware05/captains-compass-cursor/issues/288) |
| Baseline | `origin/main` @ `bb8f334` (**v1.87.2**) |
| Branch | `feature/288-audit-p2-sentry-profiles` |
| Rollback | `rollback/pre-audit-p2-sentry-profiles` @ `bb8f334` |
| Proposed release | **v1.88.0** |
| Created | 2026-11-21 |
| Approved by | Logan Ware (Captain) — 2026-11-21 |

Budget: `.agent/budgets/audit-p2-sentry-profiles.md`  
Durable copy: `docs/plans/AUDIT_P2_SENTRY_PROFILES.md`  
Evidence: `.agent/evidence/audit-p2-sentry-profiles/`

## Approval decisions

| Q | Decision |
|---|---|
| Q1 Replace active plan | **yes** |
| Q2 Include COMPASS_PROFILE v0 | **yes** |
| Q3 Prefer T3 live instead | **no** |
| Q4 Release train | **v1.88.0** |

## Scope delivered

### W1 — Sentry `window_hours`

- `build_issues_list_query` / `normalize_window_hours` in `orchestrator/integrations/sentry/client.py`
- Live list URL embeds `is:unresolved lastSeen:-{N}h`
- Hermetic mock-transport tests in `tests/orchestrator/test_sentry_window_hours.py`

### W2 — `COMPASS_PROFILE` v0

- `orchestrator/env_profiles.py` — `core` + `integrations` additive bundles
- `scripts/run-profile.sh` + `northstar profile list|show|export`
- Auto-apply when `COMPASS_PROFILE` set at northstar startup
- Doctor asserts profile export + lastSeen wiring

## Out of scope (deferred)

Specialized real eval · T3 live · B4 FIX→SUBMIT · N4 live arm · deleting individual flags

## Acceptance criteria

- [x] `window_hours` affects live Sentry request (unit test)
- [x] Fixture/hermetic Sentry tests pass; live dual-gated
- [x] Profile expand documented + tested; flags override
- [x] doctor + `tests/run.sh` green; evidence recorded
- [ ] PR from `main`; rollback tag cited (pending open)

## Validation

- Unit window_hours + profiles: pass
- `./scripts/doctor.sh`: pass
- `./tests/run.sh`: 138 passed, 0 failed
