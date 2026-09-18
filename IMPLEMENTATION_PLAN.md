# Implementation Plan — M39 / Phase B Live Cursor Agentic Security ingestion

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE on main (#175)**; follow-up opaque forge → #174 |
| Plan ID | `m39-agentic-security-phase-b` |
| Supersedes | Continues `agentic-security-review-integration` Phase B |
| Product | **NorthStar** |
| Baseline | **v1.39.1** (M38 on branch; lands after/with M38) |
| Prepared | 2026-09-18 |
| Approved | 2026-09-18 — Captain: “I approve M38/M39 plans” |
| Design source | https://cursor.com/docs/security-review ; M37 ADR-054 |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.40.0** |
| Rollback tag | `rollback/pre-m39-agentic-security-phase-b` |
| Branch | `cursor/m39-agentic-security-phase-b-5182` |
| Issue | [#170](https://github.com/loganware05/captains-compass-cursor/issues/170) |
| Linear | [OVA-54](https://linear.app/ovaltechnologysolutions/issue/OVA-54) |
| Captain | Logan Ware |

## Acceptance criteria

1. Plan-gated ✅
2. Opt-in ingest produces evidence without breaking hermetic default review ✅
3. Allowlist fail-closed when unset / disabled ✅
4. Fixture tests for severity mapping ✅
5. Docs + ADR; Skill slug `code-reviewer` unchanged ✅

## Approval gate

**APPROVED** 2026-09-18 — Captain: “I approve M38/M39 plans”.
