# Implementation Plan — M39 / Phase B Live Cursor Agentic Security ingestion

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `m39-agentic-security-phase-b` |
| Supersedes | Continues `agentic-security-review-integration` Phase B |
| Product | **NorthStar** |
| Baseline | after **v1.39.0** (M37 Phase A); prefer after M38 Phase C |
| Prepared | 2026-09-18 |
| Design source | https://cursor.com/docs/security-review ; M37 ADR-054 |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.40.0** (tentative) |
| Branch | `cursor/m39-agentic-security-phase-b-3b10` (after approval) |
| Issue | [#170](https://github.com/loganware05/captains-compass-cursor/issues/170) |
| Captain | Logan Ware |

## Goal

Opt-in path to ingest Cursor Security Reviewer / `/review-security` results into
NorthStar Code Reviewer evidence — without making Cloud Agents the hermetic default.

## Scope (MVP)

1. Document operator flow: run `/review-security` (or Automation) → export/findings
   artifact → `northstar review` companion ingest (or `scripts/` wrapper).
2. Normalize Cursor severities → NorthStar finding shapes; write under
   `.agent/evidence/review/<run-id>/agentic-security/`.
3. Allowlist gate (same posture as M30 GitHub drafts) — off by default; Captain
   enable per repo.
4. Map accepted/rejected into M31 outcomes optionally (proposal-only).
5. Hermetic fixtures for ingest parser (no live Cloud required in CI).

## Non-goals

- Replacing hermetic specialist emitters as CI default
- Auto Fix-in-Cursor / auto-merge
- Vulnerability Scanner cron productization (later)

## Acceptance criteria

1. Plan-gated
2. Opt-in ingest produces evidence without breaking hermetic default review
3. Allowlist fail-closed when unset
4. Fixture tests for severity mapping
5. Docs + ADR; Skill slug `code-reviewer` unchanged

## Approval gate

**AWAITING APPROVAL** — Captain: “I approve IMPLEMENTATION_PLAN.md for m39-agentic-security-phase-b”
(or approve after M38).
