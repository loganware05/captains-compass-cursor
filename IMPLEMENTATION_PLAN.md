# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m4-persistent-roles-bounded-autonomy
- Issue: [#50](https://github.com/loganware05/captains-compass-cursor/issues/50)
- Branch: `feature/50-m4-persistent-roles-bounded-autonomy` (merged #51)
- Target release: **v1.8.0** (released 2026-08-24)
- Created: 2026-08-24
- Last updated: 2026-08-24
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: post-approval decisions recorded below
- Rollback checkpoint: `rollback/pre-m4-persistent-roles-bounded-autonomy` @ `25fd83f`
- Feature PR: [#51](https://github.com/loganware05/captains-compass-cursor/pull/51) (merged @ `ae3b0c5`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1–M3 COMPLETE (v1.5.0–v1.7.0)
  - Baseline: **v1.7.0** (`25fd83f` / current `main` after closeout #49)
- Machine artifacts: `.agent/plans/m4-persistent-roles-bounded-autonomy/`

## Request

Proceed with **Milestone 4** of the Captain Compass multi-agent orchestration OS:
deliver Notion sequence items **11–12** — **persistent-role promotion** of specialist
subagents after measurable performance, and **bounded Level 3 autonomy** for
routing self-improvement under explicit budgets — without weakening the product
approval gate or enabling live network Technology Intelligence.

## Problem Statement

After M3:

- Subagent **proficiency / classification** metadata exists, but there is no path to
  promote a dynamic worker into a **persistent specialist role** (checked-in agent
  profile + routing affinity) based on evidence
- Experience-routing proposals remain forever proposal-only — Stage 3 autonomy
  (bounded self-tuning) is documented but not operational
- Assembler always uses the static reference-profile set; proficiency does not
  influence manifests
- High-impact changes still correctly escalate to the Captain, but there is no
  reversible, audited **apply** path for approved weight proposals

Without M4, Compass cannot graduate proven subagents or safely close the learning
loop into routing behavior.

## Desired Outcome

After M4 (v1.8.0), Captain Compass can:

1. **Propose and (Captain-approved) apply persistent-role promotions** for classified
   subagents that meet measurable thresholds (proficiency level, Experience count,
   optional Evaluation evidence) — writing/updating `.cursor/agents/` + reference
   profiles only via explicit Captain-approved PR path (never silent)
2. Prefer **Captain-approved proficient agents** in agent-manifest assembly when
   affinity matches (explainable; deterministic)
3. Support **bounded Level 3** routing updates:
   - Default remains proposal-only
   - Explicit CLI can apply a Captain-approved routing proposal to a checked-in
     `orchestrator/matcher/weights.json` (or equivalent) **only** when autonomy-budget
     limits allow and golden eval sensors still pass
4. Keep product implementation behind the existing approval gate; no live Stars TI;
   no auto-merge of Skills or agents

## Acceptance Criteria

- [x] Schema for `persistent-role-promotion` proposals + applied records
- [x] Skill `persistent-role-promotion` + CLI: propose from proficiency/Experiences;
      draft agent Markdown + reference profile under staging; Captain PR still required
      to land under `.cursor/agents/`
- [x] Measurable gates documented (e.g. proficiency ≥ proficient, N successful
      Experiences, optional evaluation winner) — tunable constants
- [x] Assembler reads Captain-approved proficiency / persistent-role registry and
      prefers matching profiles with scoring_breakdown notes
- [x] `orchestrator/matcher/weights.json` (or sidecar) loaded by `score.py` when present;
      repo ships defaults identical to today’s hard-coded WEIGHTS
- [x] Skill / CLI `apply-routing-proposal`: applies only if
      `captain_approved: true` on the proposal **and** autonomy budget allows;
      writes weights file; never mutates Skills/agents
- [x] Eval sensors: default rankings stable with default weights; apply path rejected
      without Captain flag; golden fixtures still deterministic after apply+rollback
- [x] ADR-020 for persistent roles + bounded Level 3 apply path
- [x] Doctor / install / tests / evals pass
- [x] Control-repo only; sandbox refresh after release

## Non-Goals

- Fully unsupervised overnight weight/prompt self-modification without Captain
  approval flag on each apply (even Level 3 remains Captain-flagged + budgeted)
- Live GitHub Stars / network TI in CI
- Auto-merge agent or Skill PRs
- Vector database / full Knowledge Steward productization (defer M5+)
- Changing plan-approval hook semantics for product source edits
- Replacing Cursor subagent invocation mechanics

## Assumptions

- M3 proficiency store + Experience fixtures remain the evidence substrate
- Python 3 available; stdlib-first JSON schemas
- Captains will review agent Markdown diffs before merge (same as Skill PRs)
- Level 3 “autonomy” in M4 means **budgeted apply of pre-approved proposals**, not
  free-running continuous training

## Resolved Decisions (Captain, 2026-08-24)

1. **Level 3 apply mode:** Captain flag per apply — proposal must have
   `captain_approved: true` + autonomy budget allows + evals pass. No auto-delta
   apply without per-proposal Captain flag.
2. **Persistent-role landing:** Staging drafts + Captain PR only. No
   `--captain-approved` copy into `.cursor/agents/` outside a PR merge path.
3. **Knowledge Steward:** Deferred entirely to **M5** (out of M4 scope).
4. **Target version:** **v1.8.0** confirmed.

## Current-State Analysis

| Area | State (v1.7.0) |
|---|---|
| Proficiency metadata | `.agent/agents/proficiency/` + schema; Captain flag |
| Routing proposals | `auto_apply: false`; WEIGHTS hard-coded in `score.py` |
| Candidate promotion | Ceiling `SANDBOX_TESTED` |
| Evaluator | Skill + CLI + subagent |
| Assembler | Static reference profiles only |
| Autonomy budget | Per-plan ledger; no weight-apply integration |

## Proposed Architecture

```text
.agent/agents/promotions/          # persistent-role proposals + records
.agent/routing/applied/            # audit log of applied weight proposals
orchestrator/matcher/weights.json  # checked-in defaults (optional override file)
orchestrator/agents/promote.py     # persistent-role proposal builder
orchestrator/routing/apply.py      # Captain-flagged weight apply + rollback helper
.cursor/skills/persistent-role-promotion/
.cursor/skills/bounded-autonomy/     # or extend experience-routing
scripts/propose-persistent-role.sh
scripts/apply-routing-proposal.sh
```

**Safety invariants:**

- Product plan-approval gate unchanged
- Weight apply requires Captain flag (unless Open Q1 = B) + budget + eval gate
- Persistent roles land via PR (or explicit Captain apply on feature branch only)
- Candidates remain non-executable; TI default stub

## Required Capabilities

*(Capability-plan: plan + github domains; see machine artifacts.)*

Human intent also requires: proficiency readback, persistent-role drafting,
matcher weight load/apply, autonomy-budget enforcement, evaluation gates,
assembler affinity preference.

## Reusable Capabilities Found

Top machine-ranked: `implementation-planning`, `github-integration`,
`pull-request-preparation`, plus M2/M3 Skills `experience-routing`,
`compass-evaluator`, `candidate-promotion`, `execution-telemetry`,
`autonomy-budget` (prefer these in implementation manifests).

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only.

*No external candidates queried (Technology Intelligence provider: stub).*

## Experience Signals

Informational readback (fixtures + local Experiences). Does not auto-adjust weights.

Machine artifact may list control-repo Experience ids when present.

## Task Graph

**Human-authored M4 phases:**

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| T-A | weights.json extraction + score.py loader (behavior-identical defaults) | — | no |
| T-B | Persistent-role proposal schemas + Skill/CLI + staging drafts | — | yes (vs T-A) |
| T-C | Assembler preference for Captain-approved proficient / persistent roles | T-B | no |
| T-D | Bounded apply path for routing proposals + budget/eval gates + audit log | T-A | yes (vs T-B) |
| T-E | Doctor / install / tests / evals / ADR-020 | T-A–T-D | no |
| T-F | Release prep v1.8.0 | T-E | no |

Generic planner artifact: `.agent/plans/m4-persistent-roles-bounded-autonomy/task-graph.json`

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| Discovery / architecture | `repository-scout` / `architecture-agent` | `capability-planning`, `implementation-planning` |
| Implementation | `implementation-agent` | `experience-routing`, `compass-evaluator`, `autonomy-budget` |
| Validation | `test-engineer` | `testing-validation` |
| Security | `security-reviewer` | `security-review` |
| Evaluation of apply gates | `compass-evaluator` | `compass-evaluator` |
| Documentation | `documentation-agent` | `pull-request-preparation` |

## Workstreams

1. **Matcher weights file** — extract defaults; load path; rollback helper
2. **Persistent-role promotion** — propose/draft/Captain PR path
3. **Assembler affinity** — prefer approved proficient/persistent profiles
4. **Bounded Level 3 apply** — Captain-flagged proposal apply + budget + evals
5. **Harness** — ADR-020, doctor, tests, release

## Parallelization Plan

T-A and T-B can start in parallel. T-C depends on T-B. T-D depends on T-A.
T-E integrates all. Use separate worktrees only if file boundaries stay clean
(`matcher/` vs `agents/` vs `routing/apply.py`).

## Files Expected to Change

### New

```text
orchestrator/matcher/weights.json
orchestrator/routing/apply.py
orchestrator/agents/promote.py
orchestrator/schemas/persistent-role-promotion.schema.json
.cursor/skills/persistent-role-promotion/
.cursor/skills/bounded-autonomy/   # optional; may extend experience-routing
scripts/propose-persistent-role.sh
scripts/apply-routing-proposal.sh
tests/orchestrator/test_m4_*.py
.agent/agents/promotions/.gitkeep
.agent/routing/applied/.gitkeep
```

### Modified

```text
orchestrator/matcher/score.py
orchestrator/assembler/manifest.py
orchestrator/agents/proficiency.py
.cursor/skills/experience-routing/SKILL.md
scripts/doctor.sh, scripts/install.sh
tests/run.sh, tests/evals/run.sh
DECISIONS.md, TESTING.md, README.md, PROJECT_CONTEXT.md
CHANGELOG.md, PROGRESS.md, VERSION (on release)
```

## Testing Strategy

Evidence under `.agent/evidence/m4-persistent-roles-bounded-autonomy/`.

| Layer | Action |
|---|---|
| Unit | weights load equals hard-coded defaults; apply rejects without Captain flag |
| Unit | persistent-role gates; staging drafts only |
| Integration | assembler prefers approved proficient agent when affinity matches |
| Evals | golden fixture rankings unchanged under default weights |
| Evals | after apply, rankings may change; rollback restores defaults |
| Security | path-safe IDs; no secret capture; no auto-merge |
| Rollback | tag + weights file restore |

## Security Review

- Weight apply must be auditable (who/when/proposal id)
- Persistent-role drafts must not grant elevated tools/permissions beyond existing profiles
- Budget stop must prevent apply loops

## Accessibility Review

Not applicable (no UI).

## Migration Plan

1. Product repos: `update.sh` adds Skills; default behavior unchanged until Captain
   applies a proposal or merges a persistent-role PR
2. Existing hard-coded WEIGHTS become the checked-in `weights.json` defaults
3. Forward-only upgrades

## Deployment Plan

- Merge via PR after validation
- Tag `v1.8.0`
- Sandbox `update.sh` + optional persistent-role / apply demo

## Rollback Plan

1. Restore `rollback/pre-m4-persistent-roles-bounded-autonomy`
2. Revert VERSION to 1.7.0
3. Restore default `weights.json` from tag if needed

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Ranking drift after apply | Unpredictable plans | Eval gate + rollback; Captain flag |
| Premature persistent roles | Wrong specialist defaults | Threshold gates + PR review |
| Level 3 scope creep | Unbounded autonomy | Explicit non-goals; budget stop |

## Evaluation Strategy

After implementation (post-approval), success by:

- Acceptance criteria checked
- Doctor / tests / evals green
- Default WEIGHTS behavior identical to v1.7.0 before any apply
- Apply without Captain flag fails closed
- Persistent-role drafts never appear as live agents until PR merge (or explicit apply decision)

## Learning Plan

Retain under `.agent/plans/m4-persistent-roles-bounded-autonomy/`:

- `resolve.json`, `task-graph.json`, `manifests.json`
- Link issue, branch, PR, evidence after execution

Feeds M5+ Knowledge Steward / live TI only after Captain expands scope.

## Autonomy Budget

After approval, create `.agent/budgets/m4-persistent-roles-bounded-autonomy.md`.

- Maximum iterations: 20
- Maximum failed validation cycles: 5
- Maximum estimated cost: Captain-defined
- Maximum elapsed time: 5 working days
- Maximum weight-apply operations per plan: 3 (M4-specific)
- Budget ledger path: `.agent/budgets/m4-persistent-roles-bounded-autonomy.md`

## Definition of Done

- All Acceptance Criteria checked
- Doctor / tests / evals green
- Security review recorded
- ADR-020 accepted
- PROGRESS / CHANGELOG / TESTING updated
- PR prepared with evidence
- No implementation on protected branches

## Approval Boundary

Plan is **APPROVED**. Implementation proceeds on `feature/50-m4-persistent-roles-bounded-autonomy`
only — never on protected base branches.

Machine-generated capability matches and agent manifests remain **proposals** until
Captain merges persistent-role PRs or sets `captain_approved` on routing proposals.

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-24
- **Approved revision:** Open questions resolved as above (Captain flag; staging+PR; KS→M5; v1.8.0)
- **Issue:** [#50](https://github.com/loganware05/captains-compass-cursor/issues/50)
- **Branch:** `feature/50-m4-persistent-roles-bounded-autonomy`
- **Rollback:** `rollback/pre-m4-persistent-roles-bounded-autonomy` @ `25fd83f`
