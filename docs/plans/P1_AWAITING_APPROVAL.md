# Implementation Plan — P1 (AWAITING APPROVAL)

> Promote to root `IMPLEMENTATION_PLAN.md` only after Captain approval.

## Metadata

- Status: AWAITING APPROVAL
- Plan ID: p1-commands-evidence-multiruntime
- Issue: TBD (create after approval)
- Branch: TBD `feature/<issue>-p1-commands-evidence-multiruntime`
- Created: 2026-07-30
- Last updated: 2026-07-30
- Approved by:
- Approval date:
- Approved revision:

## Request

Implement **P1** from the production-orchestration gap analysis (after P0 / v1.2.0):

1. Cursor **phase commands** (plan → implement → validate → PR → close)
2. **Evidence matrix** by change type (machine-checkable DoD hints + PR evidence)
3. **Multi-runtime** agent instruction adapters (`AGENTS.md` canonical; optional
   Claude Code / Codex-friendly pointers)

## Problem Statement

Operators re-enter the Compass pipeline via free-form chat. Evidence expectations
are a long aspirational list rather than a typed matrix. The harness is Cursor-first
while production teams increasingly compose Cursor + Claude Code / Codex on a
shared `AGENTS.md`.

## Desired Outcome

1. Six Cursor commands that wrap existing Skills/phases without new autonomy.
2. A documented evidence matrix (and light PR-hook / template wiring) so agents
   know which artifacts are required for API / UI / schema / docs / harness changes.
3. Optional multi-runtime install: keep `AGENTS.md` canonical; add thin adapters
   (`CLAUDE.md` and/or docs) that point at Compass rules without duplicating policy.
4. VERSION **1.3.0** (minor: additive commands + docs + optional adapters).

## Acceptance Criteria

### A. Phase commands

- [ ] Ship Cursor commands under `.cursor/commands/` (replace stub README):
  - `initialize-project`
  - `plan-feature`
  - `implement-approved-plan`
  - `validate-change`
  - `prepare-pr`
  - `close-workstream`
- [ ] Each command is a thin prompt/procedure that loads the relevant Skills and
      respects the approval gate (implement command refuses without APPROVED plan).
- [ ] README documents how to invoke commands.
- [ ] Installer already copies `.cursor/commands/`; doctor/tests assert the six files.

### B. Evidence matrix

- [ ] Add `docs/EVIDENCE_MATRIX.md` mapping change types → required evidence
      artifacts under `.agent/evidence/`.
- [ ] Update `templates/docs/IMPLEMENTATION_PLAN.md` Testing / Definition of Done
      to reference the matrix.
- [ ] Document matrix in PR-evidence hook README (keep soft hook fail-open).
- [ ] TESTING.md links the matrix.

Suggested minimum matrix rows:

| Change type | Required evidence (examples) |
|---|---|
| Docs / workflow-only | doctor and/or tests transcript |
| Library / API | unit/integration results |
| UI | tests + accessibility note + screenshot path |
| Schema / migration | migration plan + rollback note + test results |
| Security-sensitive | security review notes |

### C. Multi-runtime adapters

- [ ] Keep root `AGENTS.md` as the single policy source.
- [ ] Add `docs/integrations/multi-runtime-agents.md`.
- [ ] Install thin `CLAUDE.md` **only when missing** (never overwrite customized).
- [ ] Optional Codex nested-`AGENTS.md` monorepo notes (docs only in P1).
- [ ] Do **not** require adapters for doctor green.
- [ ] Prefer symlink or ≤15-line pointer files; no policy fork.

### D. Release hygiene

- [ ] VERSION `1.3.0`; CHANGELOG; ADR-015; PROGRESS/PROJECT_CONTEXT
- [ ] Evidence under `.agent/evidence/p1-commands-evidence-multiruntime/`
- [ ] Issue + branch + rollback + PR; tag/release after merge
- [ ] Sandbox refresh to 1.3.0 after release

## Non-Goals

- P2: golden-agent evals, harness GC Skill, session/cost telemetry product,
  structural-test examples, young-package supply-chain harden
- Making soft hooks fail-closed
- Building a full cross-tool memory SaaS
- Changing critical fail-closed hook policy from P0
- Soft-hook `COMPASS_SKIP_*` env inheritance fix (default **defer**; optional
  addendum if Captain wants it in P1)

## Open Questions

1. **Adapter install default:** install thin `CLAUDE.md` only when missing?
   **Recommendation:** yes.
2. **Include soft-hook skip signaling fix in P1?**
   **Recommendation:** defer unless Captain wants it.
3. **Command file format:** confirm against current Cursor docs during implementation.

## Workstreams

| ID | Workstream | Parallel? |
|---|---|---|
| W1 | Phase commands + tests/doctor | Yes vs W3 |
| W2 | Evidence matrix + plan template + docs | Yes vs W1 |
| W3 | Multi-runtime docs + optional CLAUDE.md pointer | Yes vs W1 |
| W4 | VERSION 1.3.0 + ADR + memory + evidence | After W1–W3 |

## Autonomy Budget

- Maximum iterations: 8
- Maximum failed validation cycles: 3
- Maximum elapsed minutes: 240
- Stop on scope change: true
- Ledger after approval: `.agent/budgets/p1-commands-evidence-multiruntime.md`

## Sequenced Follow-On

**P2** after P1 COMPLETE: golden-agent evals; harness GC; session ledger;
structural-test examples; young-package supply-chain harden; optional soft-hook
skip signaling harden.

## Approval Record

<!-- Captain: approve to proceed. Then promote this file to root IMPLEMENTATION_PLAN.md. -->
