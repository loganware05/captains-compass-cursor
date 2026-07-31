# Implementation Plan

## Metadata

- Status: APPROVED
- Plan ID: p1-commands-evidence-multiruntime
- Issue: [#29](https://github.com/loganware05/captains-compass-cursor/issues/29)
- Branch: `feature/29-p1-commands-evidence-multiruntime`
- Created: 2026-07-30
- Last updated: 2026-07-30
- Approved by: Captain
- Approval date: 2026-07-30
- Approved revision: P1 as drafted; CLAUDE.md only when missing; defer soft-hook COMPASS_SKIP_* fix
- Rollback checkpoint: `rollback/pre-p1-commands-evidence-multiruntime` (`ff9225d`)

## Request

Implement **P1** after v1.2.0 → **v1.3.0**.

## Acceptance Criteria

### A. Phase commands

- [x] Six commands under `.cursor/commands/`
- [x] Thin prompts; implement refuses without APPROVED plan
- [x] README documents invocation
- [x] doctor/tests assert the six files

### B. Evidence matrix

- [x] `docs/EVIDENCE_MATRIX.md`
- [x] Plan template + TESTING.md + hooks README reference matrix
- [x] Soft PR-evidence hook remains fail-open

### C. Multi-runtime adapters

- [x] `docs/integrations/multi-runtime-agents.md`
- [x] Install thin `CLAUDE.md` only when missing
- [x] Doctor does not require CLAUDE.md on products
- [x] Codex nested AGENTS notes (docs only)

### D. Release hygiene

- [x] VERSION 1.3.0; CHANGELOG; ADR-015; memory; evidence
- [x] Issue + branch + rollback
- [ ] PR merged; tag/release; sandbox refresh (Captain)

## Autonomy Budget

Ledger: `.agent/budgets/p1-commands-evidence-multiruntime.md`

## Approval Record

- Approved by: Captain on 2026-07-30
- Issue: #29
- Rollback: `rollback/pre-p1-commands-evidence-multiruntime` (`ff9225d`)
