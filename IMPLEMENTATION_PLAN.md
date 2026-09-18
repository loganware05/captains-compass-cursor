# Implementation Plan — Agentic security review in NorthStar Code Reviewer

## Metadata

| Field | Value |
|---|---|
| Status | **SHIPPED** (Phase A / v1.39.0) |
| Plan ID | `agentic-security-review-integration` |
| Supersedes | — (builds on M28 specialists + M36 hook hardening) |
| Product | **NorthStar** |
| Baseline | **v1.38.1** (M36) |
| Prepared | 2026-09-16 |
| Approved | 2026-09-17 — Captain: “I approve IMPLEMENTATION_PLAN.md for agentic-security-review-integration” |
| Design source | Cursor Security Agents docs + PR #7 Agentic Security Review findings |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.39.0** |
| Rollback tag | `rollback/pre-m37-agentic-security-review` |
| Branch | `cursor/m37-agentic-security-review-3b10` |
| Captain | Logan Ware |

## Acceptance criteria (Phase A MVP)

1. Plan-gated ✅
2. Specialist emits candidates for the two PR #7 hook bypass classes on fixture diffs ✅
3. Hermetic tests green; doctor unchanged locks ✅
4. Docs updated; ADR-054 ✅
5. No requirement on Cursor Cloud for default `northstar review` ✅

## Residual (later plans)

- Phase B — live Cursor Security Agent / `/review-security` ingestion
- Phase C — shell redirect forge gate for `IMPLEMENTATION_PLAN.md`

## Approval gate

**APPROVED** 2026-09-17 — Captain: “I approve IMPLEMENTATION_PLAN.md for agentic-security-review-integration”.
