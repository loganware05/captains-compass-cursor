# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m3-evaluator-experience-routing
- Issue: [#45](https://github.com/loganware05/captains-compass-cursor/issues/45)
- Branch: `feature/45-m3-evaluator-experience-routing`
- Target release: **v1.7.0** (additive; non-breaking)
- Created: 2026-08-23
- Last updated: 2026-08-23
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: M3 as drafted + resolved open questions (proposal-only weights, evaluator Skill+CLI+subagent proficiency, SANDBOX_TESTED candidate ceiling, v1.7.0)
- Rollback checkpoint: `rollback/pre-m3-evaluator-experience-routing` (`f36beb2`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1 COMPLETE (v1.5.0), M2 COMPLETE (v1.6.0)
  - Baseline: **v1.6.0** (`f36beb2` / current `main` after closeout #44)
- Machine artifacts: `.agent/plans/m3-evaluator-experience-routing/`

## Request

Proceed with **Milestone 3** of the Captain Compass multi-agent orchestration OS:
close the learning loop opened in M2 by adding a **Captain Compass Evaluator**,
**experience-based routing proposals**, and an **extended promotion lifecycle** —
without Level 3 autonomous self-modification or live network Technology Intelligence.

## Problem Statement

After M2:

- ExecutionRuns and Experiences are recorded but **do not influence** Skill ranking
- Candidate promotion stops at `ANALYZED`; `SECURITY_REVIEWED` / `SANDBOX_TESTED` are docs only
- Architecture calls for a **Captain Compass Evaluator** to arbitrate uncertain choices via
  bounded experiments — no Skill, schema, or CLI exists yet
- Matcher weights remain static; any Experience-driven change would require ad-hoc edits

Without M3, telemetry is write-only and promotion cannot accumulate sandbox evidence
before Captain Skill PRs.

## Desired Outcome

After M3 (v1.7.0), Captain Compass can:

1. Run **bounded evaluator experiments** (compare alternatives A/B with schemas + evidence
   under `.agent/evaluations/`) via Skill + CLI — proposals only
2. **Read** Experience / ExecutionRun stores and emit **routing proposals**
   (Skill confidence deltas, optional matcher weight suggestions) as reviewable artifacts —
   never auto-apply to live matcher weights
3. Advance candidates `ANALYZED → SECURITY_REVIEWED → SANDBOX_TESTED` with required evidence
   paths; still Captain-gated before `APPROVED` / Skill sidecar PR
4. Provide `compass-evaluator` Cursor subagent + reference profile, and a schema for
   **subagent proficiency / classification** records updated only with Captain-approved
   metadata (fed by Skills trained / Experiences)
5. Keep approval gate, hooks, and non-executable TI invariants intact

## Acceptance Criteria

- [x] `evaluation.schema.json` (+ experiment result schema) validated; directory
      `.agent/evaluations/` seeded (gitignored contents + `.gitkeep`)
- [x] Skill `compass-evaluator` (+ script `scripts/run-evaluation.sh`) can record a
      bounded comparison experiment with provenance and outcome score
- [x] Skill / module `experience-routing` reads Experiences and writes proposal JSON under
      `.agent/routing/proposals/` (Captain review; no live weight mutation)
- [x] Optional opt-in: apply a **Captain-approved** proposal file to sidecar confidence
      fields only via explicit CLI (never silent); matcher weight file remains proposal-only
      unless Captain chooses otherwise in Open Questions
- [x] `candidate-promotion` extended: `SECURITY_REVIEWED` and `SANDBOX_TESTED` stages with
      evidence requirements; still `approved_for_execution: false`
- [x] Plan writer / capability-plan may surface a short “Experience signals” readback
      section (informational; not auto-rank override)
- [x] Cursor subagent `.cursor/agents/compass-evaluator.md` + reference profile JSON
- [x] Subagent proficiency/classification schema + store under `.agent/agents/proficiency/`
      (Captain-approved metadata writes only; proposal helpers allowed)
- [x] ADR-019 (or DECISIONS entry) for evaluator + experience-routing + promotion extension
- [x] Unit + harness tests; evals prove proposals do not change default matcher scores
- [x] `./scripts/doctor.sh`, `./tests/run.sh`, `./tests/evals/run.sh` pass
- [x] No product-repo app code; control-repo only (sandbox refresh after release)

## Non-Goals

- Level 3 autonomous weight / prompt self-tuning
- Live GitHub Stars / network TI in CI
- Auto-merge Skill PRs or auto-set `approved_for_execution: true`
- Vector database / Knowledge Steward productization
- Full persistent-role promotion of dynamic workers without Captain metadata approval (Notion item 11); M3 only tracks proficiency/classification metadata
- Replacing Cursor subagent invocation mechanics
- Full ML experiment platform

## Assumptions

- Python 3 remains available
- M2 Experience fixtures and store layout are sufficient seed data
- Evaluator experiments are local/offline by default
- Capitan remains authority for any confidence or weight change landing in git

## Resolved Decisions (Captain approval 2026-08-24)

1. **Matcher weights:** Experience-routing remains **proposal-only** — never auto-apply
   to live matcher weights in M3.
2. **Evaluator surface:** Ship Skill + CLI **and** a Cursor subagent
   (`compass-evaluator`) plus **subagent proficiency / classification metadata** so that
   after sufficient Skill training, classified subagents can be tracked as proficient for
   specific task classes (Captain-approved metadata; not silent role promotion).
3. **Promotion ceilings:**
   - **Candidate capabilities:** stop at `SANDBOX_TESTED` (Captain Skill PR still required
     for `APPROVED` / live Skills).
   - **Classified subagents:** Captain-approved metadata is the ceiling for classification
     and proficiency tracking (separate from candidate Skill lifecycle).
4. **Target version:** **v1.7.0** confirmed.

## Current-State Analysis

| Area | State (v1.6.0) |
|---|---|
| Planning pipeline | Registry → resolve → task graph → manifests → plan sections |
| Telemetry | `orchestrator/telemetry/` + `record-execution-run.sh` |
| TI | stub default; file provider offline |
| Promotion | `DISCOVERED → ANALYZED` + Skill draft staging |
| Matcher | Static weights in `orchestrator/matcher/score.py` |
| Evaluator | Documented in Notion only |

## Proposed Architecture

```text
.agent/evaluations/           # experiment runs (gitignored JSON)
.agent/routing/proposals/     # experience-routing proposals (gitignored)
.agent/agents/proficiency/    # Captain-gated subagent proficiency metadata
orchestrator/evaluator/       # schemas + run_experiment + report
orchestrator/routing/         # load Experiences → proposal builders
orchestrator/promotion/       # extend lifecycle stages through SANDBOX_TESTED
orchestrator/agents/          # proficiency/classification helpers
.cursor/skills/compass-evaluator/
.cursor/skills/experience-routing/
.cursor/agents/compass-evaluator.md
orchestrator/reference-profiles/compass-evaluator.json
scripts/run-evaluation.sh
scripts/propose-experience-routing.sh
scripts/record-agent-proficiency.sh
```

**Safety invariants:**

- Default matcher behavior unchanged until Captain merges an approved change
- Candidates remain `approved_for_execution: false`
- Evaluator cannot skip plan-approval hook or mutate product source

## Required Capabilities

*(Capability-plan inference — security/test/github domains; see machine artifacts.)*

Control-repo intent also requires: evaluation recording, experience readback,
routing proposal authoring, candidate lifecycle advancement, schema validation,
doctor/evals coverage.

## Reusable Capabilities Found

Top machine-ranked Skills for the clarified objective: `security-review`,
`testing-validation`, `dependency-supply-chain`, `github-integration`,
`pull-request-preparation`, plus M2 Skills `candidate-promotion`,
`execution-telemetry`, `experience-skill-training` (lower score due to maturity).

**Human refinement:** Implementation should preferentially load
`implementation-planning`, `capability-planning`, `execution-telemetry`,
`candidate-promotion`, `testing-validation`, `security-review`, `autonomy-budget`.

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only.

*No external candidates queried (Technology Intelligence provider: stub).*

Live Stars adapters remain deferred (same as M2 non-goal).

## Task Graph

**Human-authored M3 phases** (refines generic planner output):

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| T-A | Evaluation schemas + `.agent/evaluations/` layout | — | no |
| T-B | `orchestrator/evaluator/` + `run-evaluation.sh` + Skill | T-A | no |
| T-C | Experience routing proposals module + Skill + CLI | — | yes (vs T-B) |
| T-D | Promotion through `SANDBOX_TESTED` + subagent proficiency metadata | T-A | yes (vs T-B/C) |
| T-E | Optional plan-writer “Experience signals” readback | T-C | no |
| T-F | Doctor / install / tests / evals / ADR-019 | T-B, T-C, T-D, T-E | no |
| T-G | Release prep v1.7.0 | T-F | no |

Machine artifact (generic): `.agent/plans/m3-evaluator-experience-routing/task-graph.json`

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| Discovery / architecture | `repository-scout` / `architecture-agent` | `capability-planning`, `implementation-planning` |
| Implementation | `implementation-agent` | `execution-telemetry`, `candidate-promotion`, `autonomy-budget` |
| Validation | `test-engineer` | `testing-validation` |
| Security | `security-reviewer` | `security-review`, `candidate-promotion` |
| Documentation | `documentation-agent` | `pull-request-preparation` |

Machine artifact: `.agent/plans/m3-evaluator-experience-routing/manifests.json`

## Workstreams

1. **Evaluator** — schemas, runner, Skill, evidence format
2. **Experience routing** — proposal generator; optional apply path per Open Q1
3. **Promotion extension** — lifecycle + evidence gates
4. **Harness** — doctor, tests, evals, ADR, docs, release

## Parallelization Plan

T-B, T-C, and T-D may proceed in parallel after T-A schemas land, using separate
worktrees if needed. T-E depends on T-C. T-F integrates all.

## Files Expected to Change

### New

```text
orchestrator/schemas/evaluation.schema.json
orchestrator/evaluator/
orchestrator/routing/
.cursor/skills/compass-evaluator/
.cursor/skills/experience-routing/
scripts/run-evaluation.sh
scripts/propose-experience-routing.sh
tests/orchestrator/test_evaluator.py
tests/orchestrator/test_experience_routing.py
tests/fixtures/evaluations/
.agent/evaluations/.gitkeep
.agent/routing/proposals/.gitkeep
```

### Modified

```text
orchestrator/promotion/advance.py
orchestrator/plan_writer/render.py   # optional Experience signals section
.cursor/skills/candidate-promotion/SKILL.md
scripts/doctor.sh, scripts/install.sh
tests/run.sh, tests/evals/run.sh
DECISIONS.md, TESTING.md, README.md, PROJECT_CONTEXT.md
CHANGELOG.md, PROGRESS.md, VERSION (on release)
```

## Testing Strategy

Evidence under `.agent/evidence/m3-evaluator-experience-routing/`.

| Layer | Action |
|---|---|
| Unit | evaluation schema; proposal builder; promotion stage transitions |
| Integration | CLI smokes; capability-plan unchanged default rankings |
| Evals | sensor: default matcher scores identical with/without Experiences present |
| Security | proposals cannot flip `approved_for_execution`; path-safe IDs |
| Rollback | tag restore |

## Security Review

- Evaluations must not capture secrets from env or private evidence dirs
- Routing proposals are non-authoritative until Captain merge
- Promotion evidence paths stay under `.agent/` staging

## Accessibility Review

Not applicable (no UI).

## Migration Plan

1. Product repos: `update.sh` adds new Skills; no behavior change until used
2. Existing Experiences remain valid input for proposals
3. Matcher defaults unchanged on upgrade

## Deployment Plan

- Merge via PR after validation
- Tag `v1.7.0`
- Sandbox `update.sh` + optional evaluator / routing demo

## Rollback Plan

1. Restore `rollback/pre-m3-evaluator-experience-routing`
2. Revert VERSION to 1.6.0
3. Product repos stay on 1.6.0 until ready (forward-only updates)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Silent ranking drift | Unpredictable plans | Default scores unchanged; eval sensor |
| Over-scoped Level 3 | Autonomy creep | Explicit non-goal; proposals only |
| Promotion evidence theater | False confidence | Require file paths + schema validation |

## Evaluation Strategy

After implementation (post-approval), success by:

- Acceptance criteria checked
- Doctor / tests / evals green
- Default Skill ranking golden fixtures still deterministic
- Evaluator smoke writes schema-valid evaluation JSON
- Routing proposal smoke from `tests/fixtures/experience/`

## Learning Plan

Retain under `.agent/plans/m3-evaluator-experience-routing/`:

- `resolve.json`, `task-graph.json`, `manifests.json`
- Link issue, branch, PR, evidence after execution

Feeds Milestone 4+ (persistent-role promotion; bounded Level 3 autonomy) only after
Captain expands autonomy budget.

## Autonomy Budget

After approval, create `.agent/budgets/m3-evaluator-experience-routing.md`.

- Maximum iterations: 20
- Maximum failed validation cycles: 5
- Maximum estimated cost: Captain-defined
- Maximum elapsed time: 5 working days
- Budget ledger path: `.agent/budgets/m3-evaluator-experience-routing.md`

## Definition of Done

- All Acceptance Criteria checked
- Doctor / tests / evals green
- Security review recorded
- ADR-019 accepted
- PROGRESS / CHANGELOG / TESTING updated
- PR prepared with evidence
- No implementation on protected branches

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Machine-generated capability matches and agent manifests are **proposals** only.
The Captain may approve, revise, or reject before any product implementation proceeds.

Approval means:

1. Record approval below (and resolve open questions as needed)
2. Set Status to **APPROVED**
3. Create GitHub issue
4. Create rollback tag
5. Create feature branch `feature/<issue>-m3-evaluator-experience-routing`
6. Begin Phase T-A

Until then, only planning documents and discovery artifacts may change.

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-24
- **Approved revision:** M3 evaluator + experience-routing (proposal-only) + SANDBOX_TESTED candidate ceiling + compass-evaluator subagent + proficiency metadata; v1.7.0
- **Issue:** [#45](https://github.com/loganware05/captains-compass-cursor/issues/45)
- **Branch:** `feature/45-m3-evaluator-experience-routing`
- **Rollback:** `rollback/pre-m3-evaluator-experience-routing` @ `f36beb2`

**Phase T-G complete (2026-08-24):** VERSION `1.7.0`, release evidence, release PR pending.

## Completion Record

- **Completed:** 2026-08-24
- **Merged feature PR:** [#46](https://github.com/loganware05/captains-compass-cursor/pull/46) @ `a0156e8`
- **Release PR:** `chore/45-release-v1.7.0` (pending)
- **Rollback (M3 feature):** `rollback/pre-m3-evaluator-experience-routing` @ `f36beb2`
