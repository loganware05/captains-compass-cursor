# Implementation Plan — M27 NorthStar Code Reviewer MVP

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `m27-northstar-code-reviewer` |
| Supersedes | `m24-linear-skills-ledger` (CLOSED — shipped as v1.29.0 / v1.29.1) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.29.1` / `main` @ `6d78312` |
| Prepared | 2026-09-12 |
| Design source | ChatGPT NorthStar Code Reviewer brief (uploaded); copy planned under `docs/design/NorthStar_Code_Reviewer.md` after approval |
| Product target | `loganware05/captain-compass-sandbox` for dry-run evidence only |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.30.0** (MVP slice; phased follow-ons deferred) |
| Rollback tag (post-approval) | `rollback/pre-m27-northstar-code-reviewer` |
| Branch (plan only) | `cursor/m27-northstar-code-reviewer-3b10` |
| Issue | *TBD after approval* |
| Approved by | *pending* |
| Approval date | *pending* |
| Approved revision | *pending* |

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

## Current-state summary

| Surface | Today |
|---|---|
| Review agents | `adversarial-reviewer`, `security-reviewer`, `accessibility-reviewer` (manual) |
| Review Skills | `security-review`, `accessibility-review`, `review-fix-loop` (consumes external feedback), `testing-validation` |
| Judge | `compass-evaluator` (evaluations under `.agent/evaluations/`) |
| GitHub | Stage 1 via `github-integration`; webhook: `ping` / `issues` / `issue_comment` only |
| CI | Control `.github/workflows/ci.yml` = doctor + tests; no PR review bot |
| Reputation | Experience → RoutingProposal confidence deltas (Captain-gated); **no finding precision** |
| Gap | No `orchestrator/review/`, no `code-reviewer` Skill, no report schema, no `northstar review` CLI |

## Desired outcomes

### MVP pipeline (this plan)

```
PR / branch / local diff
        ↓
 Review Orchestrator (CLI + Skill)
        ↓
 Detect domains + load intent (plan / issue / AC)
        ↓
 Investigate (diff + related files + callers + tests)
        ↓
 Deterministic tools (lint/type/test when available — optional, fail-soft)
        ↓
 Multi-skill findings (compose existing review Skills/agents as procedures)
        ↓
 Verify / Judge (discard unverified / low-confidence)
        ↓
 Evidence report only (.agent/evidence/code-review/<id>/)
```

### Differentiators locked for MVP

1. **Intent vs implementation** — load approved `IMPLEMENTATION_PLAN.md` (and optional
   issue body) and score findings that cite unmet acceptance criteria / scope drift.
2. **Compose, don’t reimplement** — route through existing Skills/agents rather than
   a monolithic “LLM reviews the diff” prompt.
3. **Evidence-first** — default output is a structured report + Markdown summary;
   **no automatic GitHub review comments** in MVP.
4. **Verification gate** — findings below confidence threshold or lacking evidence
   paths are discarded or marked `unverified` (not posted).

### Deferred (explicit non-goals for v1.30.0)

- Auto-posting GitHub Pull Request Reviews / inline comments
- Webhook `pull_request` event handling
- Auto-spawn repair agent / FIND→FIX→TEST→SUBMIT loop
- First-class skill-precision reputation store (TP/FP ledger)
- Multi-forge (GitLab/Bitbucket) or commercial multi-tenant SaaS

## Acceptance criteria

1. New Skill `.cursor/skills/code-reviewer/` (+ capability sidecar) documents the
   four-stage procedure and when to invoke it.
2. Optional subagent `.cursor/agents/code-reviewer.md` + reference profile exist and
   are doctor-listed.
3. `orchestrator/review/` implements hermetic stages:
   - **detect** — domain hints from paths/diff + intent artifacts
   - **investigate** — assemble context pack (diff, related paths, plan excerpt)
   - **verify** — filter/rank candidate findings with confidence + evidence refs
   - **report** — write JSON (schema-validated) + Markdown under
     `.agent/evidence/code-review/<run-id>/`
4. Schema `orchestrator/schemas/code-review-report.schema.json` validates reports
   (findings with severity, confidence, evidence paths, skill provenance, status
   `verified|unverified|discarded`).
5. CLI `scripts/run-code-review.sh` and launcher `northstar review …` run against a
   local git range or fixture pack without network.
6. Unit tests cover detect/investigate/verify/report with fixtures under
   `tests/fixtures/code-review/`.
7. Sandbox dry-run: produce at least one evidence report against
   `captain-compass-sandbox` (fixture branch or `main…HEAD` synthetic pack) without
   posting to GitHub.
8. Docs: integration note + EVIDENCE_MATRIX row; PROGRESS/CHANGELOG/DECISIONS updated
   on ship.
9. Doctor + `./tests/run.sh` green; no secrets committed.
10. Default posture remains **no auto-merge** and **no auto GitHub review posts**.

## Non-goals

- Replacing Cursor Bugbot / CodeRabbit commercially
- Training a custom coding model
- Posting review comments without a later Captain-approved phase
- Expanding product allowlist beyond sandbox for live ingress
- Auto-applying matcher weight changes from review outcomes

## Assumptions

1. Control repo remains source of truth for Skills/orchestrator; sandbox is the
   dry-run target (ADR-041 topology).
2. MVP may use **heuristic + structured LLM-ready packs** in Python; live model
   calls are optional behind an explicit flag and default **off** in CI (fixtures
   supply candidate findings for verify/report tests).
3. Captain approval of this plan authorizes control-repo scaffolding + sandbox
   evidence dry-run only.
4. Capability-plan machine output for this objective over-weighted React UI; the
   **human task graph below supersedes** that inference.

## Open questions (Captain decisions requested)

1. **MVP model invocation:** Keep CI fully hermetic (fixture findings only), or allow
   an opt-in `--invoke-model` path for local Captain runs?
2. **Naming:** Skill slug `code-reviewer` vs `northstar-code-review`?
   *(Recommendation: `code-reviewer`.)*
3. **Phase B priority after MVP:** (a) GitHub review posting, (b) PR webhook detect,
   (c) precision/reputation ledger, (d) repair-agent loop?
4. **Issue tracker:** Create GitHub issue only, or also a Linear parent under an
   existing project?

## Current-state analysis

Discovery (2026-09-12) confirmed:

- Strong manual review stack; weak orchestration.
- Ingress deliberately narrow — extending webhooks is a material scope expand.
- Experience/Evaluation schemas can store lessons today; precision metrics need a
  dedicated schema later.
- Best MVP posture: **CLI + Skill + schema + hermetic pipeline**, compose existing
  reviewers, evidence-only.

## Proposed architecture

```
scripts/run-code-review.sh
        │
        ▼
orchestrator/review/
  ├── detect.py          # domains, intent artifacts, changed paths
  ├── investigate.py     # context pack (diff, neighbors, plan/AC excerpt)
  ├── verify.py          # confidence filter, evidence requirements
  ├── report.py          # JSON + Markdown writers
  └── pipeline.py        # stage orchestration
        │
        ▼
.agent/evidence/code-review/<run-id>/
  ├── report.json        # schema: code-review-report
  ├── report.md
  └── context-pack.json  # optional debug
```

**Skill `code-reviewer`** instructs agents to:

1. Run the CLI (or equivalent stages) against the active branch/PR.
2. Load plan/issue intent.
3. Optionally dispatch specialist agents (`security-reviewer`, `adversarial-reviewer`,
   `accessibility-reviewer`) and fold their findings into `verify`.
4. Hand verified findings to humans or to `review-fix-loop` — never auto-merge.

**Intent check (MVP):** extract acceptance criteria / non-goals from
`IMPLEMENTATION_PLAN.md` when present; emit `scope-drift` / `unmet-criterion`
candidate findings when diff clearly contradicts them (heuristic + optional model).

## Required Capabilities

Human-corrected for this objective (machine plan over-inferred React UI):

- implementation-plan-authoring / approval-gate-enforcement
- repository-discovery / source-code-context
- github-integration (read PR/diff metadata; no review post in MVP)
- security-review / testing-validation / review-fix-loop
- compass-evaluator (judge patterns)
- execution-telemetry (optional Experience writeback)
- autonomy-budget / worktree-orchestration
- node-engineering / python orchestrator patterns (control CLI)

Machine artifact retained: `.agent/plans/m27-northstar-code-reviewer/resolve.json`

## Reusable Capabilities Found

Highest-relevance approved Skills (from capability-plan + discovery):

| Skill | Role in MVP |
|---|---|
| `repository-discovery` | Investigation context |
| `source-code-context` | Cross-file / API truth |
| `security-review` | Security specialist findings |
| `testing-validation` | Deterministic verification hooks |
| `accessibility-review` | UI-change path |
| `review-fix-loop` | Downstream consumer of verified findings |
| `github-integration` | Diff/PR metadata (read) |
| `pull-request-preparation` | Evidence packaging adjacency |
| `compass-evaluator` | Judge / arbitration patterns |
| `execution-telemetry` | Optional run/Experience records |
| `experience-routing` | Future reputation (deferred apply) |
| `implementation-planning` | Intent artifact authoring |
| `capability-planning` | Domain → Skill selection |

### Capability Gaps

No blocking gap for scaffolding. **New capability to introduce:** orchestrated
`code-review` (Skill + module). Deferred gaps: GitHub review API wrapper,
finding-precision ledger, PR webhook detect.

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only.

*No external candidates queried (TI provider: stub). Future learning may ingest
Semgrep/OWASP/React review procedures via the existing Stars→Skills flywheel —
out of MVP scope.*

## Task Graph

**Human-authored** (supersedes machine `task-impl-frontend` graph):

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| `task-discovery` | Confirm file boundaries, schemas, doctor hooks, fixture strategy | — | no |
| `task-architecture` | Lock report schema + pipeline contracts + rollback | task-discovery | no |
| `task-impl-pipeline` | Implement `orchestrator/review/` + schema + CLI + launcher | task-architecture | no |
| `task-impl-skill` | Add Skill, agent, reference profile, doctor/registry wiring | task-architecture | yes (with pipeline after schema freeze) |
| `task-validation` | Unit tests + doctor + control tests + sandbox dry-run evidence | task-impl-pipeline, task-impl-skill | no |
| `task-documentation` | Docs, ADR, PROGRESS, CHANGELOG, EVIDENCE_MATRIX | task-validation | no |

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| `task-discovery` | `repository-scout` | `repository-discovery`, `capability-planning` |
| `task-architecture` | `architecture-agent` | `capability-planning`, `security-review` |
| `task-impl-pipeline` | `implementation-agent` | `node-engineering` (CLI), `testing-validation`, `autonomy-budget` |
| `task-impl-skill` | `implementation-agent` | `skill-lifecycle`, `code-structure-cleanup` |
| `task-validation` | `test-engineer` + `adversarial-reviewer` | `testing-validation`, `security-review` |
| `task-documentation` | `documentation-agent` | `pull-request-preparation`, `github-integration` |

## Workstreams

1. **WS-A — Contracts:** schema + fixtures + pipeline interfaces
2. **WS-B — Orchestrator + CLI:** detect/investigate/verify/report + `northstar review`
3. **WS-C — Skill/agent packaging:** installable Compass surface + doctor
4. **WS-D — Validation & docs:** tests, sandbox dry-run, memory docs

WS-B and WS-C may proceed in parallel after schema freeze.

## Parallelization Plan

Use one worktree on `cursor/m27-northstar-code-reviewer-3b10` unless WS-B/C conflict;
prefer sequential commits on a single branch for MVP cohesion.

## Files expected to change (post-approval)

| Path | Change |
|---|---|
| `orchestrator/review/**` | New pipeline module |
| `orchestrator/schemas/code-review-report.schema.json` | New |
| `scripts/run-code-review.sh` | New |
| `scripts/northstar` | Add `review` subcommand |
| `.cursor/skills/code-reviewer/**` | New Skill + sidecar |
| `.cursor/agents/code-reviewer.md` | New |
| `orchestrator/reference-profiles/code-reviewer.json` | New |
| `scripts/doctor.sh` / registry compile inputs | List new agent/skill |
| `tests/orchestrator/test_*code_review*.py` | New |
| `tests/fixtures/code-review/**` | New |
| `docs/integrations/code-reviewer.md` (or design note) | New |
| `docs/design/NorthStar_Code_Reviewer.md` | Design source archive |
| `docs/EVIDENCE_MATRIX.md` | New row |
| `DECISIONS.md` / `PROGRESS.md` / `CHANGELOG.md` / `PROJECT_CONTEXT.md` | Memory |
| `VERSION` | Bump to `1.30.0` on ship |

Sandbox: evidence only under `.agent/evidence/…` unless a separate approved demo
plan requires product code changes.

## Testing strategy

| Layer | Plan |
|---|---|
| Unit | Pipeline stages with fixture diffs + candidate findings |
| Schema | `validate.py` / unittest against valid & invalid reports |
| Control | `./scripts/doctor.sh` + `./tests/run.sh` |
| Integration | CLI end-to-end on fixture pack (no network) |
| Sandbox dry-run | Evidence report path recorded under `.agent/evidence/m27-northstar-code-reviewer/` |
| Security | Review CLI for path traversal / secret leakage in context packs |
| Accessibility | N/A (no UI) |
| Adversarial | Fresh-context pass on pipeline + Skill prose |

## Security review

- Context packs must redact secrets (reuse ingress/event redaction patterns).
- No webhook secret handling in MVP.
- Fixture mode must not shell out to untrusted paths.
- Report paths confined under repo `.agent/evidence/`.

## Accessibility review

Not applicable (no UI surfaces).

## Migration plan

Additive only. Existing Skills/agents unchanged in behavior. Installer picks up new
Skill/agent on next install/update into product repos.

## Deployment plan

1. Merge control PR → tag `v1.30.0`
2. Optional sandbox install/update to receive Skill
3. Phase B (GitHub posting) requires a **new** approved plan

## Rollback plan

1. Tag `rollback/pre-m27-northstar-code-reviewer` at approval start
2. Revert merge commit / restore prior VERSION
3. Remove Skill via update from previous tag if installed into sandbox
4. No data migrations; delete evidence directories if undesired

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Noisy false positives | Verification gate; evidence required; default no GitHub posts |
| Scope creep into Bugbot clone | Hard non-goals; Phase B gated |
| Model nondeterminism in CI | Hermetic fixtures; model opt-in only |
| Topology confusion | CLI in control; `--repo` / `northstar review --repo` |
| Planner React misfire | Human task graph supersedes machine graph |

## Evaluation strategy

- Schema + unit tests green
- Fixture run produces ≥1 verified and ≥1 discarded finding (proves filter)
- Sandbox dry-run evidence committed or summarized
- Adversarial review: no CRITICAL/HIGH unresolved
- Doctor clean

## Learning plan

- Retain `.agent/plans/m27-northstar-code-reviewer/`
- Optional Experience write for dry-run (proposal-only routing)
- Phase C may feed precision into skill reputation (not this plan)

## Autonomy budget

After approval, create `.agent/budgets/m27-northstar-code-reviewer.md`.

| Limit | Value |
|---|---|
| Maximum iterations | 12 |
| Maximum wall-clock (agent) | Stop at budget; write Budget Stop Report |
| Maximum cost | Track qualitatively; stop if thrashing on fixtures |
| Max scope expands | 0 without returning to approval gate |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Machine-generated capability matches are proposals only. The Captain may approve,
revise scope (especially Open Questions), or reject.

## Definition of Done

- Acceptance criteria 1–10 satisfied
- Validation evidence under `.agent/evidence/m27-northstar-code-reviewer/`
- Docs/memory updated
- PR ready against `main`
- First Mate adversarial inspection complete

---

## Captain approval checklist

Please reply with approval (and any locks on Open Questions), for example:

> Approved — M27 NorthStar Code Reviewer MVP as written.
> Locks: hermetic CI (no model in CI); Skill slug `code-reviewer`; Phase B = GitHub posting next; GitHub issue only.
