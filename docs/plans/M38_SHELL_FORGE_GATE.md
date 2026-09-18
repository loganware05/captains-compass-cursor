# Implementation Plan — M38 / Phase C Shell forge gate

> Durable plan archive for `m38-shell-forge-gate` (do not overwrite from a rotated root plan).

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED — IMPLEMENTING** |
| Plan ID | `m38-shell-forge-gate` |
| Baseline | **v1.39.0** |
| Approved | 2026-09-18 — Captain: “I approve M38/M39 plans” |
| Release | **v1.39.1** |
| Branch | `cursor/m38-shell-forge-gate-5182` |
| Issue | [#169](https://github.com/loganware05/captains-compass-cursor/issues/169) |
| Linear | [OVA-53](https://linear.app/ovaltechnologysolutions/issue/OVA-53) |

## Scope (done)

1. `plan-approval-check.sh` on `beforeShellExecution` — deny promoting forges unless Captain env
2. Hermetic tests + ADR-055 + product APPLY note

## Residual

- Opaque `cat file > IMPLEMENTATION_PLAN.md` without promote tokens in argv
- M39 live Cursor Security ingest (separate plan)
