# XRV W2 — Eight-Pillar Repository Readiness Assessor

> **AWAITING APPROVAL** — Issue [#263](https://github.com/loganware05/captains-compass-cursor/issues/263).
> After Captain approval, copy/activate into repo-root `IMPLEMENTATION_PLAN.md`.

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `xrv-readiness-assessor` |
| Issue | [#263](https://github.com/loganware05/captains-compass-cursor/issues/263) |
| Baseline | **v1.83.1** @ `dece600` |
| Proposed release | **v1.84.0** |
| Prior | W1 `xrv-release-integrity` (#261/#262) **COMPLETE** |

## Problem

XRV needs measurable eight-pillar readiness (Software Factory model) that separates
**repository readiness** from **NorthStar effectiveness**, scoring only from
verifiable evidence.

## Desired outcome

Gated hermetic `northstar assess readiness` (name TBD) with schema-validated
scorecard, authority locks false, doctor fail-closed, fixtures + tests.

## Out of scope

Live providers, Level 3, auto-promotion, TrapHouse/Bitcoin product edits.

## Acceptance

- Fail-closed without gate
- Dual score sections (readiness vs effectiveness)
- No invented scores; missing evidence → unscored/blocked
- Doctor + unit tests + docs/ADR

## Captain decision

Reply: `Approve xrv-readiness-assessor as written` (or with changes).
