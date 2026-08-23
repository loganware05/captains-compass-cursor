# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m2-execution-telemetry-ti
- Issue: [#41](https://github.com/loganware05/captains-compass-cursor/issues/41)
- Branch: `feature/41-m2-execution-telemetry-ti`
- Target release: **v1.6.0** (additive; non-breaking)
- Created: 2026-08-22
- Last updated: 2026-08-23
- Approved by: Captain
- Approval date: 2026-08-23
- Approved revision: M2 as drafted + resolved open questions (experience dual-path, Stars-shaped fixtures, Captain-approved Skill sidecar PR, v1.6.0)
- Rollback checkpoint: `rollback/pre-m2-execution-telemetry-ti` (`c8f978d`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Meta prompt: Foundation Implementation (Milestone 1 shipped; M2 continues deferred items)
  - Prior plan: M1 capability-aware planning (COMPLETE, v1.5.0)
  - Baseline: **v1.5.0** (`c8f978d` / current `main`)

## Request

Proceed with **Milestone 2** of the Captain Compass multi-agent orchestration OS:
close the gap between planning artifacts and post-execution learning by recording
**execution telemetry**, optionally wiring a **file-backed Technology Intelligence**
provider (still not executable), and adding a **Captain-gated candidate promotion**
path — without autonomous product execution or Level 3 self-modification.

## Problem Statement

Milestone 1 ships capability-aware planning (registry → resolve → task graph →
manifests → plan sections) and stops at the approval gate. After implementation:

- `ExecutionRun` schema exists but is never populated
- `.agent/runs/` is gitignored with no writer API or Skill procedure
- There is no append-only **Experience** store linking outcomes to Skills/tasks
- Technology Intelligence remains a stub (`[]`); no fixture/file provider for local demos
- Candidate lifecycle (`DISCOVERED → … → PROVEN_SKILL`) is documentation only

Without M2, planning cannot learn from completed workstreams, and TI remains
untestable except as an empty stub.

## Desired Outcome

After M2 (v1.6.0), Captain Compass can:

1. Record validated `ExecutionRun` JSON at workstream close (Git provenance: issue,
   branch, commits, PR, outcome, Skills used)
2. Append summarized **Experience** records for future planning/readback
3. Optionally load TI candidates from a **file catalog** behind an explicit config
   flag (CI stays offline; candidates still **NOT APPROVED FOR EXECUTION**)
4. Promote a candidate sidecar `DISCOVERED → ANALYZED`, then open a **Captain-approved
   Skill sidecar PR** path into `.cursor/skills/<slug>/` — never auto-execute or
   auto-merge
5. Support **two Experience instances**: (a) control-repo test fixtures by default;
   (b) `experience-skill-training` Skill that imports a production-repo Experience
   sample, drafts a Skill candidate in the control repo, and runs control-repo tests
   before any Captain approval
6. Keep the existing approval gate, hooks, and post-approval implementation model

## Acceptance Criteria

- [x] `experience.schema.json` (+ any needed `ExecutionRun` field extensions) validated
- [x] `orchestrator/telemetry/` (or equivalent) can create/load ExecutionRuns under
      `.agent/runs/<run-id>.json` and Experiences under `.agent/experience/`
- [x] CLI: `scripts/record-execution-run.sh` (and thin Python module) accepts plan-id /
      Git refs / outcome and writes schema-valid artifacts
- [x] Skills `close-workstream` / `pull-request-preparation` (and/or new
      `execution-telemetry` Skill) instruct First Mate to record runs on completion
- [x] File-backed TI provider: `FileTechnologyIntelligenceProvider` reading
      `orchestrator/providers/technology_intelligence/fixtures/*.json` (or
      `.agent/capabilities/candidates/`) when
      `COMPASS_TI_PROVIDER=file` (default remains `stub`)
- [x] Plan writer continues to render **NOT APPROVED FOR EXECUTION**; file provider
      never sets `approved_for_execution: true`
- [x] Candidate promotion Skill + script: validate schema, advance lifecycle to
      `ANALYZED`, write staging sidecar; support Captain-approved Skill sidecar PR
      (still never auto-merge / auto-execute)
- [x] `experience-skill-training` Skill: import production Experience → draft Skill
      under control-repo staging → run control-repo tests; commit Experiences in
      control-repo **tests/fixtures** by default (not product-repo by default)
- [x] TI fixtures are **redacted Stars-shaped** offline samples
- [x] Doctor / install seed `.agent/runs/` layout (gitignored contents) and
      `.agent/experience/.gitkeep` as needed
- [x] Unit + harness tests; evals prove stub default + file provider offline fixtures
- [x] ADR-018 (or DECISIONS entry) for telemetry + TI file provider decisions
- [x] `./scripts/doctor.sh`, `./tests/run.sh`, `./tests/evals/run.sh` pass
- [x] No product-repo app code changes; control-repo only (sandbox refresh after release)

## Non-Goals

- Autonomous product execution beyond today's `/implement-approved-plan` machinery
- Live GitHub Stars / network TI in CI (file fixtures only in M2)
- Auto-promotion to `AVAILABLE_SKILL` / `PROVEN_SKILL` without Captain approval
- Auto-install or execute external repositories
- Vector databases, ML routing, persistent Knowledge Steward agent
- Level 3 self-improvement (auto-tuning matcher weights)
- Evaluator experiment runner productization
- Replacing Cursor subagent invocation mechanics

## Assumptions

- Python 3 remains available (hooks / orchestrator already require it)
- M2 remains **control-repo** infrastructure; product repos get Skill/template updates via install/update
- Git evidence is available locally via `git` / `gh` when recording runs (graceful degrade if missing)
- File TI fixtures are curated, checked-in, offline samples — not scraped live data
- Matcher score updates from Experience remain **manual/readback** in M2 (no auto weight tuning)

## Resolved Decisions (Captain approval 2026-08-23)

1. **Experience dual-path:** By default, commit Experience samples in **control-repo
   tests only**. Additionally ship Skill `experience-skill-training` so a Captain can
   import an Experience from a **production** repo, draft/train a Skill candidate in
   the control repo, and validate with control-repo tests before approval.
2. **TI fixtures:** Use **redacted Stars-shaped** offline samples (GitHub Star
   Categorization-compatible shape, no live network).
3. **Promotion ceiling:** Allow a **Captain-approved Skill sidecar PR** into
   `.cursor/skills/<slug>/` after staging `ANALYZED` — never auto-merge or execute.
4. **Target version:** **v1.6.0** confirmed.

## Current-State Analysis

| Asset | M1 state | M2 need |
|---|---|---|
| `execution-run.schema.json` | Stub schema | Writer + Skill + tests |
| Experience schema | Absent | Add |
| `.agent/runs/` | Gitignored, unused | Writer API |
| TI provider | Stub only | File provider + flag |
| Candidate lifecycle | Docs only | Promote DISCOVERED→ANALYZED tooling |
| `/close-workstream` | Docs update only | Call telemetry recorder |
| Approval gate / hooks | Unchanged | Must remain unchanged |

## Proposed Architecture

```text
orchestrator/
  telemetry/
    record.py           # build ExecutionRun + Experience from inputs
    store.py            # write/read .agent/runs + .agent/experience
  experience/
    schema (JSON Schema)
  providers/technology_intelligence/
    stub.py (existing)
    file_provider.py    # NEW — offline fixtures
    fixtures/           # curated candidate JSON
    validate.py (existing)
  promotion/
    advance.py          # DISCOVERED → ANALYZED staging + draft Skill PR prep
  training/
    from_experience.py  # import product Experience → control-repo Skill draft

scripts/
  record-execution-run.sh
  ti-discover.sh        # optional: run provider and print candidates
  promote-candidate.sh  # staging lifecycle advance
  train-skill-from-experience.sh

.cursor/skills/
  execution-telemetry/       # NEW
  candidate-promotion/       # NEW (Captain-gated)
  experience-skill-training/ # NEW (product Experience → control training)
```

**Config:**

| Variable | Default | Effect |
|---|---|---|
| `COMPASS_TI_PROVIDER` | `stub` | `stub` \| `file` |
| `COMPASS_TI_FIXTURES_DIR` | package fixtures | Override fixture path |

**Safety invariants (unchanged):**

- Candidates never enter Skill ranking or agent manifests as approved Skills
- `approved_for_execution` remains schema-const `false`
- Plan-approval hook behavior unchanged

## Required Capabilities

Inferred from the objective and repository context.

- implementation-plan-authoring
- approval-gate-enforcement
- scope-definition
- rollback-planning
- github-issue-create
- github-pr-create
- pr-description-assembly

**Domains detected:** plan, github

## Reusable Capabilities Found

Approved Compass Skills ranked for this objective (deterministic matcher).

| Skill | Score | Notes |
|---|---:|---|
| `implementation-planning` | 0.5571 | capability_overlap=0.2571 |
| `github-integration` | 0.4286 | lifecycle_stage=0.15 |
| `pull-request-preparation` | 0.3643 | lifecycle_stage=0.15 |
| `capability-planning` | 0.3 | lifecycle_stage=0.15 |
| `testing-validation` | 0.3 | lifecycle_stage=0.15 |
| `security-review` | 0.3 | lifecycle_stage=0.15 |
| `autonomy-budget` | 0.3 | lifecycle_stage=0.15 |
| `harness-gc` | 0.3 | lifecycle_stage=0.15 |

### Capability Gaps

No capability gaps detected for the inferred requirements.

*(Human note: M2 adds Skills `execution-telemetry`, `candidate-promotion`, and
`experience-skill-training` with sidecars — registry count becomes 27.)*

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only.

*No external candidates queried (Technology Intelligence provider: stub).*

*(M2 will add a file provider so this section can demonstrate offline fixtures
without network access; banner and non-execution rules remain mandatory.)*

## Task Graph

| ID | Objective | Depends on | Parallelizable |
|---|---|---|---|
| T-A | Schemas: Experience + ExecutionRun extensions; store layout | — | — |
| T-B | Telemetry writer + `record-execution-run.sh` + unit tests | T-A | — |
| T-C | Skills: `execution-telemetry`; wire close-workstream / PR prep | T-B | — |
| T-D | File TI provider + fixtures + config flag + plan_writer wiring | — | yes (vs T-B) |
| T-E | Candidate promotion (→ANALYZED + Captain Skill sidecar PR path) | T-D | — |
| T-E2 | `experience-skill-training` Skill + CLI (product → control) | T-B | yes (vs T-E) |
| T-F | Doctor/install/evals/docs/ADR; sandbox checklist row | T-C, T-E, T-E2 | — |
| T-G | Release prep v1.6.0 | T-F | — |

Machine artifacts: `.agent/plans/m2-execution-telemetry-ti/{resolve,task-graph,manifests}.json`

## Proposed Agent Configuration

| Task | Reference profile | Skills | Model class | Rationale |
|---|---|---|---|---|
| T-A–B | `architecture-agent` / `implementation-agent` | `capability-planning`, `implementation-planning` | reasoning-strong / coding-strong | Schemas + telemetry module |
| T-C | `documentation-agent` | `execution-telemetry`, `pull-request-preparation` | fast-iter | Skill + command wiring |
| T-D–E | `security-reviewer` + `implementation-agent` | `security-review`, `dependency-supply-chain` | coding-strong | TI/promotion safety |
| T-F | `test-engineer` | `testing-validation`, `harness-gc` | coding-strong | Deterministic sensors |
| Final review | `adversarial-reviewer` | — | inherit | Scope/safety gap review |

## Workstreams

Single sequential workstream on one feature branch (shared harness files).
T-D may proceed in parallel with T-B after T-A schemas land if using a worktree
with clear file boundaries (`providers/` vs `telemetry/`).

## Parallelization Plan

Optional parallel worktrees after approval:

- Worktree A: `telemetry/` + Skills close-workstream
- Worktree B: `providers/technology_intelligence/file_provider.py` + promotion

Do not parallelize doctor/tests/CHANGELOG edits.

## Files Expected to Change

### New

```text
orchestrator/schemas/experience.schema.json
orchestrator/telemetry/*.py
orchestrator/promotion/*.py
orchestrator/providers/technology_intelligence/file_provider.py
orchestrator/providers/technology_intelligence/fixtures/*.json
.cursor/skills/execution-telemetry/{SKILL.md,capability.yaml}
.cursor/skills/candidate-promotion/{SKILL.md,capability.yaml}
.cursor/skills/experience-skill-training/{SKILL.md,capability.yaml}
scripts/record-execution-run.sh
scripts/promote-candidate.sh
scripts/train-skill-from-experience.sh
tests/orchestrator/test_telemetry.py
tests/orchestrator/test_file_ti_provider.py
tests/orchestrator/test_promotion.py
tests/orchestrator/test_experience_training.py
tests/fixtures/experience/*.json
.agent/experience/.gitkeep
```

### Modified

```text
orchestrator/plan_writer/build.py          # provider selection
orchestrator/schemas/execution-run.schema.json  # if fields needed
.cursor/commands/close-workstream.md
.cursor/skills/pull-request-preparation/SKILL.md
scripts/doctor.sh, scripts/install.sh
tests/run.sh, tests/evals/run.sh
docs/integrations/technology-intelligence.md
DECISIONS.md (ADR-018)
PROGRESS.md, CHANGELOG.md, TESTING.md, README.md, PROJECT_CONTEXT.md
VERSION (on release)
```

### Explicitly not modified

- `.cursor/hooks/plan-approval-check.sh` behavior
- Matcher auto-weight tuning
- Live network scrapers

## Testing Strategy

Evidence under `.agent/evidence/m2-execution-telemetry-ti/` per
`docs/EVIDENCE_MATRIX.md` (control-repo infrastructure).

| Layer | Action |
|---|---|
| Unit | telemetry write/read; schema validation; file TI fixtures; promotion staging |
| Integration | `record-execution-run.sh` smoke; capability-plan with `COMPASS_TI_PROVIDER=file` |
| Evals | default stub isolation; file provider offline; runs dir layout |
| Security | candidates cannot approve execution; path traversal rejected; no secrets in fixtures |
| Approval gate | DRAFT still denies product edits |
| Install smoke | temp product gets new Skills + dirs |
| Rollback | tag restore |

## Security Review

- File TI fixtures must not embed tokens/credentials
- Promotion writes only to staging paths, never silently into approved Skills
- Provider selection fail-closed to stub on unknown config values
- Experience/run JSON must not capture `.env` contents or private keys

## Accessibility Review

Not applicable (no UI). Docs remain structured Markdown.

## Migration Plan

1. Product repos: `update.sh` adds new Skills; optional — run telemetry on next close
2. Existing plans without ExecutionRuns remain valid
3. Default TI stays stub — no behavior change until Captain sets `COMPASS_TI_PROVIDER=file`

## Deployment Plan

- Merge via PR after validation
- Tag `v1.6.0`
- Sandbox `update.sh` + checklist row for telemetry + optional file TI demo

## Rollback Plan

1. Restore `rollback/pre-m2-execution-telemetry-ti`
2. Revert VERSION to 1.5.0
3. Product repos stay on 1.5.0 until ready (forward-only updates)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Scope creep into live Stars API | Network/secrets in CI | File fixtures only; ADR |
| Telemetry noise / PII | Privacy | Schema allowlist fields; scrub paths |
| Promotion mistaken for install | Safety | Staging-only; Captain PR for Skill add |
| Matcher auto-tune temptation | Unbounded learning | Explicit non-goal |

## Evaluation Strategy

After implementation (post-approval), Captain Compass will determine success by:

- Matching task acceptance criteria from the task graph
- Applicable validation layers from `TESTING.md` / evidence matrix
- Security and accessibility reviews when manifests include those tasks
- Adversarial review before merge when scope is non-trivial
- Comparison of outcome vs inferred required capabilities

Capability planning quality for this plan is evaluated by:

- Explicit capability gaps (must not be silent)
- Deterministic Skill ranking reproducibility
- Inspectable agent manifest rationale per task

**M2-specific success checks:**

1. Same fixture inputs → identical ExecutionRun field shapes (deterministic)
2. `COMPASS_TI_PROVIDER=stub` → empty candidates (regression)
3. `COMPASS_TI_PROVIDER=file` → fixture candidates + NOT APPROVED banner
4. Promotion of approved-for-execution=true fixture **fails closed**

## Learning Plan

Retain under `.agent/plans/m2-execution-telemetry-ti/`:

- `.agent/plans/m2-execution-telemetry-ti/resolve.json`
- `.agent/plans/m2-execution-telemetry-ti/task-graph.json`
- `.agent/plans/m2-execution-telemetry-ti/manifests.json`
- Link to issue, branch, PR, tests, and evaluation evidence after execution

Use ExecutionRun / Experience population in M2 to enable Milestone 3+ routing
improvements (still Captain-gated; no Level 3 auto-tune in M2).

## Autonomy Budget

After approval, create `.agent/budgets/m2-execution-telemetry-ti.md`.

- Maximum iterations: 20
- Maximum failed validation cycles: 5
- Maximum estimated cost: Captain-defined
- Maximum elapsed time: 5 working days
- Budget ledger path: `.agent/budgets/m2-execution-telemetry-ti.md`
- On limit: `.agent/evidence/m2-execution-telemetry-ti/BUDGET_STOP_REPORT.md`

## Definition of Done

- All Acceptance Criteria checked
- Doctor / tests / evals green
- Security review recorded under `.agent/evidence/m2-execution-telemetry-ti/`
- ADR-018 accepted
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
5. Create feature branch `feature/<issue>-m2-execution-telemetry-ti`
6. Begin Phase T-A

Until then, only planning documents and discovery artifacts may change.

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-23
- **Approved revision:** M2 execution telemetry + file TI + promotion + experience-skill-training; v1.6.0
- **Issue:** [#41](https://github.com/loganware05/captains-compass-cursor/issues/41)
- **Branch:** `feature/41-m2-execution-telemetry-ti`
- **Rollback:** `rollback/pre-m2-execution-telemetry-ti` @ `c8f978d`

**Phase T-G complete (2026-08-23):** VERSION `1.6.0`, release evidence, release PR pending.

## Completion Record

- **Completed:** 2026-08-23
- **Merged feature PR:** [#42](https://github.com/loganware05/captains-compass-cursor/pull/42) @ `ccd4e61`
- **Release PR:** `chore/41-release-v1.6.0` (pending)
- **Rollback (M2 feature):** `rollback/pre-m2-execution-telemetry-ti` @ `c8f978d`
- **Rollback (pre-v1.6.0 VERSION):** `rollback/pre-v1.6.0` @ `ccd4e61` (tag at release)
