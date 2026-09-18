# Implementation Plan — M38 / Phase C Shell forge gate

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED — IMPLEMENTING** |
| Plan ID | `m38-shell-forge-gate` |
| Supersedes | Completes ADR-053 residual + M37 Phase C |
| Product | **NorthStar** |
| Baseline | **v1.39.0** tagged after #172 |
| Prepared | 2026-09-18 |
| Approved | 2026-09-18 — Captain: “I approve M38/M39 plans” |
| Design source | ADR-053 residual; Cursor Agentic Security Review class (shell bypass of plan gate) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.39.1** |
| Rollback tag | `rollback/pre-m38-shell-forge-gate` |
| Branch | `cursor/m38-shell-forge-gate-5182` |
| Issue | [#169](https://github.com/loganware05/captains-compass-cursor/issues/169) |
| Linear | [OVA-53](https://linear.app/ovaltechnologysolutions/issue/OVA-53) |
| Captain | Logan Ware |

## Acceptance criteria

1. Plan-gated ✅
2. Shell forge promoting APPROVED without Captain env → deny ✅
3. Captain env / non-promoting plan edits → allow ✅
4. Hermetic tests + doctor green ✅
5. Docs/ADR update; product hook refresh note ✅

## Approval gate

**APPROVED** 2026-09-18 — Captain: “I approve M38/M39 plans”.
