# Implementation Plan — M27 NorthStar Code Reviewer MVP

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED — IMPLEMENTING / VALIDATED** |
| Plan ID | `m27-northstar-code-reviewer` |
| Supersedes | `m24-linear-skills-ledger` (CLOSED — shipped as v1.29.0 / v1.29.1) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.29.1` / plan-only commit `153d29d` |
| Prepared | 2026-09-12 |
| Design source | ChatGPT NorthStar Code Reviewer brief; archived under `.agent/evidence/m27-northstar-code-reviewer/design-source.md` |
| Product target | `loganware05/captain-compass-sandbox` for dry-run evidence only |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.30.0** (MVP slice; phased follow-ons deferred) |
| Rollback tag | `rollback/pre-m27-northstar-code-reviewer` @ `153d29d` |
| Branch | `cursor/m27-northstar-code-reviewer-3b10` |
| Issue | https://github.com/loganware05/captains-compass-cursor/issues/141 |
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-09-12 |
| Approved revision | plan + locks as stated in Captain approval message |

## Captain locks (binding)

1. **Hermetic CI** — fixture findings only; no model calls in CI
2. **Skill slug** — `code-reviewer`
3. **Phase B next** — GitHub review posting (separate plan)
4. **Tracker** — GitHub issue only (#141)

## Request (Captain-level)

Begin creating and integrating a **NorthStar Code Reviewer** capability aligned with
the ChatGPT architecture brief: not “another CodeRabbit,” but a
**Detection → Investigation → Verification → Review** pipeline that understands the
engineering system that produced the change (intent vs implementation), composes
existing NorthStar Skills/agents, and keeps false positives low by verifying before
emitting findings.

## Problem statement

1. NorthStar already has review **building blocks** (adversarial/security/a11y
   agents, `testing-validation`, `review-fix-loop`, `compass-evaluator`, GitHub
   Stage 1) but **no orchestrated code-review capability**.
2. Commercial reviewers compete on context + verification + signal-to-noise.
   NorthStar’s unusual advantage is **intent-aware** review:
   `IMPLEMENTATION_PLAN` / issue / Skills used / commits → PR — not only old vs new
   code.
3. GitHub ingress today supports **issues intake + approve comments only**;
   `pull_request` events are unsupported. There is no review-report schema, CLI, or
   Skill that runs the four-stage pipeline.
4. Without a deliberate MVP, agents will keep reinventing one-off review prompts,
   posting noisy comments, or skipping verification.

## Desired outcomes (MVP)

```
PR / branch / local diff
        ↓
 Review Orchestrator (CLI + Skill)
        ↓
 Detect domains + load intent (plan / issue / AC)
        ↓
 Investigate (diff + related files + plan excerpt)
        ↓
 Multi-skill / heuristic candidate findings (fixtures in CI)
        ↓
 Verify / Judge (discard unverified / low-confidence)
        ↓
 Evidence report only (.agent/evidence/code-review/<id>/)
```

### Deferred (non-goals for v1.30.0)

- Auto-posting GitHub Pull Request Reviews / inline comments
- Webhook `pull_request` event handling
- Auto-spawn repair agent / FIND→FIX→TEST→SUBMIT loop
- First-class skill-precision reputation store (TP/FP ledger)

## Acceptance criteria

1. Skill `.cursor/skills/code-reviewer/` (+ capability sidecar) documents the
   four-stage procedure.
2. Agent `.cursor/agents/code-reviewer.md` + reference profile exist and are
   doctor-listed.
3. `orchestrator/review/` implements hermetic stages detect → investigate →
   verify → report.
4. Schema `orchestrator/schemas/code-review-report.schema.json` validates reports.
5. CLI `scripts/run-code-review.sh` and `northstar review …` run without network.
6. Unit tests + fixtures under `tests/fixtures/code-review/`.
7. Sandbox dry-run evidence under `.agent/evidence/m27-northstar-code-reviewer/`.
8. Docs + EVIDENCE_MATRIX + DECISIONS/PROGRESS/CHANGELOG updated; VERSION 1.30.0.
9. Doctor + orchestrator unit tests green; no secrets committed.
10. Default posture: **no auto-merge** and **no auto GitHub review posts**.

## Architecture

```
scripts/run-code-review.sh
        │
        ▼
orchestrator/review/
  ├── detect.py
  ├── investigate.py
  ├── verify.py
  ├── report.py
  └── pipeline.py
        │
        ▼
.agent/evidence/code-review/<run-id>/
  ├── report.json
  ├── report.md
  └── context-pack.json
```

## Task Graph

| Task ID | Objective | Dependencies |
|---|---|---|
| `task-discovery` | Confirm file boundaries | — |
| `task-architecture` | Lock report schema + contracts | task-discovery |
| `task-impl-pipeline` | Implement review module + CLI | task-architecture |
| `task-impl-skill` | Skill, agent, doctor wiring | task-architecture |
| `task-validation` | Tests + sandbox dry-run | task-impl-* |
| `task-documentation` | Docs + memory | task-validation |

## Autonomy budget

After approval: `.agent/budgets/m27-northstar-code-reviewer.md`

| Limit | Value |
|---|---|
| Maximum iterations | 12 |
| Scope expands | 0 without returning to approval gate |

## Approval Boundary

**Approved 2026-09-12.** Implementation authorized under Captain locks above.
Phase B (GitHub posting) requires a **new** plan.
