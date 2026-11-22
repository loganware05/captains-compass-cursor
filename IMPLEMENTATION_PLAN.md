# Implementation Plan — Audit P2 Sentry Polish & COMPASS Profiles v0

- Status: **COMPLETE**

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `audit-p2-sentry-profiles` |
| Issue | [#288](https://github.com/loganware05/captains-compass-cursor/issues/288) |
| PR | [#289](https://github.com/loganware05/captains-compass-cursor/pull/289) **MERGED** |
| Merge commit | `c069554` |
| Rollback | `rollback/pre-audit-p2-sentry-profiles` @ `bb8f334` |
| Release | **v1.88.0** @ `c069554` |
| Approved by | Logan Ware (Captain) — 2026-11-21 |
| Completed | 2026-11-21 |

Durable: `docs/plans/AUDIT_P2_SENTRY_PROFILES.md`  
Evidence: `.agent/evidence/audit-p2-sentry-profiles/`  
Release evidence: `.agent/evidence/release-v1.88.0/`

## Delivered

1. Live Sentry Issues list embeds `--window-hours` as `lastSeen:-Nh` (1–8760).
2. Additive `COMPASS_PROFILE=core|integrations` v0 (individual flags win; no live dual-gates).
3. `northstar profile list|show|export` + auto-apply when `COMPASS_PROFILE` is set.
4. Docs, doctor asserts, ADR-111, hermetic tests.

## Follow-ups

- Deferred audit backlog: specialized real eval, T3 live, B4 FIX→SUBMIT
- **#278:** Bend entry-state law, P4/P5 history, Lean pin, ADR-110 go/no-go
