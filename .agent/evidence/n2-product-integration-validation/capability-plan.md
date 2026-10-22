## Required Capabilities

Inferred from the objective and repository context.

- implementation-plan-authoring


**Domains detected:** general

## Reusable Capabilities Found

Approved Compass Skills ranked for this objective (deterministic matcher).

| Skill | Score | Notes |
|---|---:|---|
| `implementation-planning` | 0.75 | capability_overlap=0.45 |
| `accessibility-review` | 0.3 | lifecycle_stage=0.15 |
| `autonomy-budget` | 0.3 | lifecycle_stage=0.15 |
| `capability-planning` | 0.3 | lifecycle_stage=0.15 |
| `code-structure-cleanup` | 0.3 | lifecycle_stage=0.15 |
| `dependency-supply-chain` | 0.3 | lifecycle_stage=0.15 |
| `docker-cloud` | 0.3 | lifecycle_stage=0.15 |
| `github-integration` | 0.3 | lifecycle_stage=0.15 |
| `harness-gc` | 0.3 | lifecycle_stage=0.15 |
| `ios-engineering` | 0.3 | lifecycle_stage=0.15 |
| `linear-integration` | 0.3 | lifecycle_stage=0.15 |
| `node-engineering` | 0.3 | lifecycle_stage=0.15 |
| `notion-integration` | 0.3 | lifecycle_stage=0.15 |
| `playwright-browser-validation` | 0.3 | lifecycle_stage=0.15 |
| `postgres-prisma` | 0.3 | lifecycle_stage=0.15 |
| `project-overseer` | 0.3 | lifecycle_stage=0.15 |
| `pull-request-preparation` | 0.3 | lifecycle_stage=0.15 |
| `python-ml` | 0.3 | lifecycle_stage=0.15 |
| `react-engineering` | 0.3 | lifecycle_stage=0.15 |
| `repository-discovery` | 0.3 | lifecycle_stage=0.15 |
| `review-fix-loop` | 0.3 | lifecycle_stage=0.15 |
| `security-review` | 0.3 | lifecycle_stage=0.15 |
| `source-code-context` | 0.3 | lifecycle_stage=0.15 |
| `testing-validation` | 0.3 | lifecycle_stage=0.15 |
| `worktree-orchestration` | 0.3 | lifecycle_stage=0.15 |
| `agent-skills-packaging` | 0.255 | lifecycle_stage=0.105 |
| `bounded-autonomy` | 0.255 | lifecycle_stage=0.105 |
| `candidate-promotion` | 0.255 | lifecycle_stage=0.105 |
| `code-reviewer` | 0.255 | lifecycle_stage=0.105 |
| `compass-evaluator` | 0.255 | lifecycle_stage=0.105 |
| `context-inodes` | 0.255 | lifecycle_stage=0.105 |
| `embedding-providers` | 0.255 | lifecycle_stage=0.105 |
| `execution-telemetry` | 0.255 | lifecycle_stage=0.105 |
| `experience-routing` | 0.255 | lifecycle_stage=0.105 |
| `experience-skill-training` | 0.255 | lifecycle_stage=0.105 |
| `external-knowledge-ingest` | 0.255 | lifecycle_stage=0.105 |
| `goose-agent-orchestration` | 0.255 | lifecycle_stage=0.105 |
| `hosted-vector-db` | 0.255 | lifecycle_stage=0.105 |
| `knowledge-steward` | 0.255 | lifecycle_stage=0.105 |
| `northstar-connected-routine` | 0.255 | lifecycle_stage=0.105 |
| `package-registry-ti` | 0.255 | lifecycle_stage=0.105 |
| `persistent-role-promotion` | 0.255 | lifecycle_stage=0.105 |
| `procedure-playbooks` | 0.255 | lifecycle_stage=0.105 |
| `security-audit-procedures` | 0.255 | lifecycle_stage=0.105 |
| `skill-learning-loop` | 0.255 | lifecycle_stage=0.105 |
| `skill-lifecycle` | 0.255 | lifecycle_stage=0.105 |
| `technology-intelligence-live` | 0.255 | lifecycle_stage=0.105 |

### Capability Gaps

No capability gaps detected for the inferred requirements.

## Decision Shadow (observe-only)

> Optional DecisionProvider comparison vs the deterministic matcher. Full artifact lives under `.agent/evidence/` only; this section references path/ID. Apply requires `COMPASS_DECISION_APPLY=1` and passing Noul/confidence gates (M43); default remains matcher-only.

*No decision provider run (stub, or both `COMPASS_DECISION_SHADOW` and `COMPASS_DECISION_APPLY` unset).*

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only.

*No external candidates queried (Technology Intelligence provider: stub).*

## Experience Signals

Informational readback from Experience fixtures/stores. **Does not auto-adjust matcher weights** (proposal-only via Skill `experience-routing`).

| Experience | Outcome | Skills |
|---|---|---|
| `exp-fixture-contact-counter` | success | `react-engineering`, `testing-validation`, `accessibility-review`, `capability-planning` |
| `exp-1b9f5ca5fe28` | success | — |
| `exp-21ea5b5d3d1e` | success | — |
| `exp-8c4bc301b6ba` | success | `implementation-planning` |
| `exp-f93743104ebc` | success | — |

## Knowledge Context

Informational readback from `.agent/knowledge/` (keyword search). **Does not alter Skill rankings or matcher weights.** Populate via explicit `./scripts/ingest-knowledge.sh`.

*No knowledge items matched this objective (store empty or no index).*

## Performance Context

Informational readback from `kind: performance` knowledge items. **Does not alter Skill rankings or matcher weights.** Populate via `./scripts/ingest-knowledge.sh --from-store runs,experience`.

*No performance knowledge items matched this objective.*

## Procedure Context

Informational readback from `kind: procedure` knowledge items. **Does not alter Skill rankings or matcher weights.** Populate via `./scripts/ingest-knowledge.sh --from-store procedures`.

*No procedure knowledge items matched this objective.*

## Artifact Context

Informational readback from `kind: artifact` knowledge items. **Does not alter Skill rankings or matcher weights.** Populate via `./scripts/ingest-knowledge.sh` (routing/evaluations stores).

*No artifact knowledge items matched this objective.*

## Task Graph

Execution order: task-discovery → task-architecture → task-implementation → task-validation → task-documentation

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| `task-discovery` | Discover repository structure, tooling, risks, and conventions | — | no |
| `task-architecture` | Define components, contracts, data changes, and rollback strategy | task-discovery | no |
| `task-implementation` | Implement approved changes for: Add accessible CompassStatusBadge showing NorthStar workflow v1.71.1 on the sandbox home page | task-architecture (hard) | no |
| `task-validation` | Run applicable validation layers and capture evidence | task-implementation (symlink) | no |
| `task-documentation` | Update project memory docs and completion records | task-validation | no |

Machine artifact: `.agent/plans/n2-sandbox-badge/task-graph.json`

## Proposed Agent Configuration

One manifest per task. Reference profiles map to existing `.cursor/agents/` templates.

| Task | Profile | Model class | Skills | Rationale |
|---|---|---|---|---|
| `task-discovery` | `repository-scout` | reasoning-strong | `repository-discovery`, `capability-planning`, `harness-gc` | Task 'task-discovery' requires [repo-structure-mapping, tooling-identification, convention-discovery]. Reference profile 'repository-scout' with model class 'reasoning-strong'. Selected Skills: [repository-discovery, capability-planning, harness-gc]. |
| `task-architecture` | `architecture-agent` | reasoning-strong | `capability-planning`, `code-structure-cleanup`, `dependency-supply-chain` | Task 'task-architecture' requires [component-boundary-design, api-contract-definition, migration-rollback-strategy]. Reference profile 'architecture-agent' with model class 'reasoning-strong'. Selected Skills: [capability-planning, code-structure-cleanup, dependency-supply-chain]. |
| `task-implementation` | `implementation-agent` | inherit | `autonomy-budget`, `code-structure-cleanup`, `docker-cloud` | Task 'task-implementation' requires [feature-implementation, convention-following]. Reference profile 'implementation-agent' with model class 'inherit'. Selected Skills: [autonomy-budget, code-structure-cleanup, docker-cloud]. |
| `task-validation` | `test-engineer` | coding-strong | `testing-validation`, `accessibility-review`, `ios-engineering` | Task 'task-validation' requires [unit-test-execution, integration-test-execution, definition-of-done-validation, validation-evidence-capture]. Reference profile 'test-engineer' with model class 'coding-strong'. Selected Skills: [testing-validation, accessibility-review, ios-engineering]. |
| `task-documentation` | `documentation-agent` | fast-iter | `pull-request-preparation`, `autonomy-budget`, `github-integration` | Task 'task-documentation' requires [project-memory-update, progress-tracking, completion-reporting]. Reference profile 'documentation-agent' with model class 'fast-iter'. Selected Skills: [pull-request-preparation, autonomy-budget, github-integration]. |

Machine artifact: `.agent/plans/n2-sandbox-badge/manifests.json`

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

## Learning Plan

Retain under `.agent/plans/n2-sandbox-badge/`:

- .agent/plans/n2-sandbox-badge/resolve.json
- .agent/plans/n2-sandbox-badge/task-graph.json
- .agent/plans/n2-sandbox-badge/manifests.json
- Link to issue, branch, PR, tests, and evaluation evidence after execution

Use execution evidence in Milestone 2+ to tune Skill confidence and routing.

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Machine-generated capability matches and agent manifests are **proposals** only. The Captain may approve, revise, or reject before any product implementation proceeds.

