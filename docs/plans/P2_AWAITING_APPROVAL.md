# Implementation Plan — P2 (AWAITING APPROVAL)

> Promote to root `IMPLEMENTATION_PLAN.md` only after Captain approval.

## Metadata

- Status: AWAITING APPROVAL
- Plan ID: p2-evals-harness-gc-session-supplychain
- Issue: TBD (create after approval)
- Branch: TBD `feature/<issue>-p2-evals-harness-gc-session`
- Created: 2026-07-30
- Last updated: 2026-07-30
- Approved by:
- Approval date:
- Approved revision:

## Request

Implement **P2** from the production-orchestration gap analysis (after P1 / v1.3.0):

1. **Golden-agent evals** — sandbox/control regression pack for harness behavior
2. **Harness GC Skill** — detect drift between rules, Skills, commands, docs
3. **Session / cost ledger** — lightweight phase-boundary session notes
4. **Structural-test examples** — ArchUnit / dependency-cruiser / import-linter style samples
5. **Young-package supply-chain harden** — Captain-gated dependency adds for young/unproven packages
6. **Optional:** soft-hook `COMPASS_SKIP_*` signaling that works under Cursor’s hook runner
   (env inheritance gap found during v1.2.0 sandbox publish)

Ship as **v1.4.0** (minor: additive Skills/docs/examples + installer/doctor checks).

## Problem Statement

P0/P1 made the harness safer and easier to operate, but Compass still lacks:

- Repeatable **behavioral evals** that prove agents respect the approval gate and DoD
- A **garbage-collection** loop when rules/Skills/commands/docs drift
- Lightweight **session observability** for postmortems and budget honesty
- **Computational** architecture feedback examples product repos can copy
- Stronger **supply-chain** gates when agents add young dependencies
- Reliable soft-hook skip signaling when Cursor does not forward shell env to hooks

## Desired Outcome

1. A small eval suite (scripts + docs) runnable in CI or locally that checks
   installer/doctor/hooks plus documented agent-behavior checklists for sandbox.
2. Skill `harness-gc` that proposes evidence-backed harness cleanup under a
   **separate** approved plan when product files would change (or docs-only fixes
   when safe).
3. Session note template under `.agent/sessions/` (or `.agent/runs/`) written at
   phase boundaries by First Mate / commands.
4. `examples/structural-tests/` with 1–2 concrete linter configs + README.
5. Skill or Skill extension for young-package review (age/stars/lockfile/OSV
   guidance) requiring Captain approval before adding such deps.
6. Soft-hook improvement: honor `COMPASS_SKIP_*=1` when present **in the command
   string** (and/or a `.agent/COMPASS_SKIP_HOOKS` marker), not only process env.
7. VERSION **1.4.0**; ADR-016; sandbox refresh after release.

## Acceptance Criteria

### A. Golden-agent evals

- [ ] `tests/evals/` or `docs/evals/` + runnable script covering at least:
  - Plan-approval hook deny on DRAFT / allow on APPROVED (already partly in `tests/run.sh` — extend or wrap)
  - failClosed critical/soft split
  - Installer creates commands, budgets, evidence matrix, CLAUDE.md-when-missing
  - Documented manual sandbox checklist for agent behavior (gate, no-weaken-tests)
- [ ] CI runs the automated portion (extend `.github/workflows/ci.yml` or add job)
- [ ] TESTING.md documents how to run evals

### B. Harness GC Skill

- [ ] `.cursor/skills/harness-gc/SKILL.md`
- [ ] Procedure: compare rules ↔ Skills ↔ commands ↔ README/AGENTS for contradictions;
      propose a report under `.agent/evidence/`; product file changes require a
      **separate** approved plan
- [ ] Doctor lists the Skill

### C. Session / cost ledger

- [ ] Template `templates/agent/SESSION_NOTE.md`
- [ ] Installer creates `.agent/sessions/` (gitignored private optional)
- [ ] Document in `autonomy-budget` Skill and/or phase commands that First Mate
      appends a short note at phase boundaries
- [ ] No requirement for exact token spend APIs (estimates labeled)

### D. Structural-test examples

- [ ] `examples/structural-tests/README.md` with at least one JS/TS example
      (e.g. dependency-cruiser or eslint boundaries) and optional second stack note
- [ ] Linked from README or examples index

### E. Young-package supply-chain

- [ ] Skill `dependency-supply-chain` (or section in `source-code-context`) requiring:
  - Captain approval before adding young/low-provenance packages
  - Lockfile present
  - Optional OSV/`npm audit` guidance
- [ ] Documented thresholds as **guidance** (not brittle magic numbers in hooks)

### F. Soft-hook skip signaling (include in P2)

- [ ] `pre-commit-formatting`, `pre-push-tests`, and `pr-evidence-validation` also
      allow when the **command string** contains `COMPASS_SKIP_FORMAT=1` /
      `COMPASS_SKIP_TESTS=1` / `COMPASS_SKIP_PR_EVIDENCE=1`, or when
      `.agent/COMPASS_SKIP_HOOKS` exists
- [ ] Hooks README documents the three skip mechanisms (env, command prefix, marker file)
- [ ] Tests cover command-string skip detection

### G. Release hygiene

- [ ] VERSION `1.4.0`; CHANGELOG; ADR-016; PROGRESS/PROJECT_CONTEXT
- [ ] Evidence under `.agent/evidence/p2-evals-harness-gc-session/`
- [ ] Issue + branch + rollback + PR; tag/release; sandbox refresh

## Non-Goals

- Auto-evolving harness without Captain approval
- Full telemetry SaaS / cloud cost APIs
- Making soft hooks fail-closed
- Replacing AGENTS.md with proprietary memory products
- Large new always-on rules (prefer Skills)

## Assumptions

1. Eval automation stays bash/python aligned with existing `tests/run.sh`.
2. Soft-hook command-string skip is acceptable because Captains/agents already
   document skips in transcripts.
3. Young-package policy is advisory + Skill-enforced, not a hard registry blocklist.

## Open Questions

1. **Eval depth:** automated hooks/installer only vs also a scripted “agent prompt”
   dry-run? **Recommendation:** automated harness sensors + manual sandbox
   behavioral checklist (no flaky LLM-in-CI).
2. **Supply-chain thresholds:** document “<90 days or <500 GitHub stars → Captain
   approval” as guidance? **Recommendation:** yes, labeled guidance.
3. **Session path:** `.agent/sessions/` vs reuse `.agent/runs/`?  
   **Recommendation:** `.agent/sessions/` for human-readable notes; keep `.agent/runs/`
   for machine traces if added later.

## Workstreams

| ID | Workstream | Parallel? |
|---|---|---|
| W1 | Evals + CI | Yes vs W3/W4 |
| W2 | Soft-hook skip signaling + tests | Yes vs W1 |
| W3 | harness-gc Skill | Yes |
| W4 | Session template + installer | Yes |
| W5 | Structural-test examples | Yes |
| W6 | dependency-supply-chain Skill | Yes |
| W7 | VERSION 1.4.0 + ADR + memory | After W1–W6 |

## Autonomy Budget

- Maximum iterations: 10
- Maximum failed validation cycles: 3
- Maximum elapsed minutes: 360
- Stop on scope change: true
- Ledger after approval: `.agent/budgets/p2-evals-harness-gc-session.md`

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| LLM-in-CI flaky evals | Keep CI deterministic (hooks/scripts only) |
| Over-strict supply-chain blocking Captains | Guidance + Skill; no hard hook deny in P2 |
| Harness GC proposes huge cleanup | Require separate approved plan for product edits |

## Sequenced Follow-On

None required after P2 for the original gap roadmap; future work is backlog.

## Approval Record

<!-- Captain: approve to proceed. Then promote to root IMPLEMENTATION_PLAN.md. -->
