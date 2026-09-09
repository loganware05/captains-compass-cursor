# Progress

## Current status

**M22 IN PROGRESS** — NorthStar unattended connected ops → **v1.27.0**

| Item | Value |
|---|---|
| Plan | `IMPLEMENTATION_PLAN.md` — **APPROVED — M22 IMPLEMENTATION IN PROGRESS** |
| Plan ID | `m22-m23-northstar-ops-ti-flywheel` |
| Baseline | `v1.26.0` |
| Target | **v1.27.0** (M22); M23 → v1.28.0 deferred |
| Branch | `cursor/m22-northstar-unattended-ops-6044` |
| Rollback | `rollback/pre-m22-northstar-ops` |
| Product scope | Sandbox only (`loganware05/captain-compass-sandbox`) |

## Completed

- v1.5.0–v1.26.0 / M1–M21 + #50 M4 bridge
- M21 NorthStar connected operations (fixture routine)
- Sandbox refresh through Compass **1.26.0** (sandbox#40–#42)
- Issue #50 closed; Notion MCP desktop auth for research
- Captain APPROVED M22/M23 plan 2026-09-09

## Next

1. Finish M22: live adapters + GitHub ingress + sandbox allowlist + tests/docs
2. Validate (`doctor`, M22/M21/M4 unit tests, `tests/run.sh`) + evidence
3. Sandbox refresh to Compass **1.27.0** + tag/release after merge
4. Then M23 (TI scorecard + skill flywheel) under same plan

## Blockers

None — start gate open for M22.
