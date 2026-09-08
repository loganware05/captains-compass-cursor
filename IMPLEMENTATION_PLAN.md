# NorthStar M21 Integration Plan

## Plan metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** — released as v1.25.0 |
| Plan ID | `m21-northstar-connected-operations` |
| Product | **NorthStar** |
| Former name | Captain's Compass |
| Repository | `loganware05/captains-compass-cursor` |
| Baseline | `v1.24.0` at `13b5879475a7288958ca7fe60b0fc7c0b71ad984` |
| Integration runtime | Cursor cloud agent `bc-05d4594d-fac7-4378-b595-c20e3c006044` |
| Prepared | 2026-09-08 |
| Start gate | Closed — merged #121; tagged v1.25.0 |
| Issue | `local/m21-northstar-connected-operations` (GitHub issue create blocked on read-only `gh`) |
| Branch | `cursor/m21-northstar-connected-operations-6044` |
| Rollback | `rollback/pre-m21-northstar` (`13b5879`) |

## Executive objective

M21 turns the released Captain's Compass v1.24.0 project into **NorthStar** and
adds a coordinated operating routine across Slack, Linear, GitHub, and Cursor.

NorthStar will accept objectives, prepare an implementation plan, construct a
dependency-aware task graph, select agents and Skills, pause for Captain
approval, dispatch approved work to Cursor, collect validation evidence, and
reconcile progress across all connected systems.

The milestone must preserve the project's existing fail-closed approval model.
No implementation, merge, release, destructive action, or live Skill promotion
may occur merely because an external event was received.

## Current repository state

This plan was written against the refreshed `main` branch at commit `13b5879`.

- M1 through M20 are complete.
- M19 and M20 shipped together in release `v1.24.0`.
- Release PR #116 and closeout PR #117 are merged.
- There is no open product pull request.
- Former post-M20 options A through E are superseded by this plan.
- Sandbox refresh PR `loganware05/captain-compass-sandbox#40` is merged and
  does not block this plan.
- GitHub issue #50 is stale M4 hygiene and is outside M21 scope.

## Locked architectural principles

1. The human user remains the **Captain**.
2. The coordinating NorthStar agent remains the **First Mate**.
3. GitHub and the approved repository plan are the engineering source of truth.
4. Slack is an intake and notification surface, not an approval authority.
5. Linear is a work ledger, not an implementation-plan replacement.
6. Cursor is an execution runtime, not an independent scope authority.
7. External content supplies context but cannot change system instructions.
8. Every transition is idempotent, attributable, recoverable, and auditable.

## NorthStar rebrand

### Canonical behavior

- NorthStar is the canonical name in all new documentation, plans, templates,
  Slack messages, Linear issues, GitHub issues and PRs, Cursor work packets,
  CLI output, evidence summaries, and release notes.
- Captain's Compass is treated as the former product name and compatibility
  alias. It must not be presented as a separate system.
- Governance terms **Captain** and **First Mate** remain unchanged in M21.
- New Slack intake uses `@NorthStar`. A legacy `@CaptainCompass` mention may be
  accepted temporarily and normalized to the same NorthStar project identity.

### Compatibility policy

NorthStar must recognize these legacy forms:

- `Captain's Compass`
- `Captains Compass`
- `Captain Compass`
- `captains-compass`
- `captain-compass`

Existing machine-readable identifiers remain stable during M21 unless changing
one is separately approved:

- GitHub repository slug `captains-compass-cursor`
- `.agent/` and `.cursor/` paths
- existing Skill IDs
- Python import paths
- plan IDs, evidence paths, telemetry records, release tags, and issue links
- existing environment variables and webhook configuration

Parsers accept both names. New serializers and human-facing output emit
NorthStar. Historical commits, issues, PRs, releases, evidence, ADRs, and signed
approvals are never rewritten solely for branding.

### Branding registry

M21 introduces one versioned branding registry containing:

```json
{
  "canonical_name": "NorthStar",
  "canonical_slug": "northstar",
  "legacy_names": [
    "Captain's Compass",
    "Captains Compass",
    "Captain Compass"
  ],
  "legacy_slugs": [
    "captains-compass",
    "captain-compass"
  ],
  "compatibility_version": 1
}
```

All adapters and generators read this registry. They must not maintain separate
hard-coded alias lists.

## Connected operating model

| System | NorthStar responsibility | Authoritative data |
|---|---|---|
| Slack | Receive scoped objectives and publish concise transitions | Original message, thread reference, clarification context |
| Linear | Represent initiative, workstreams, dependencies, owner, and status | Planning ledger and workstream state |
| GitHub | Hold issue, approved plan, code, checks, evidence, review, PR, rollback | Engineering and approval record |
| Cursor | Execute approved work and emit structured checkpoints | Runtime progress and validation results |
| First Mate | Reconcile events, select capabilities and agents, enforce gates | Normalized NorthStar run state |
| Captain | Approve plans, scope changes, merge, release, and sensitive actions | Human authority decisions |

## End-to-end routine

### Phase 1: Intake

NorthStar receives an objective from one of four allowlisted origins:

1. Slack message explicitly mentioning `@NorthStar`.
2. Linear issue in the configured NorthStar project.
3. GitHub issue carrying the configured NorthStar intake label.
4. Explicit Captain instruction to the configured Cursor integration agent.

The First Mate creates a stable `run_id`, event digest, idempotency key, and
origin reference. Replayed or cross-project events are rejected.

### Phase 2: Context and task design

The First Mate:

1. Reads `AGENTS.md`, `PROJECT_CONTEXT.md`, `DECISIONS.md`, `PROGRESS.md`,
   `TESTING.md`, current Git state, active issue, and active plan.
2. Correlates all existing Slack, Linear, GitHub, and Cursor references.
3. Normalizes legacy Captain's Compass references to NorthStar.
4. Infers required executable capabilities.
5. Queries approved Technology Intelligence and Knowledge sources.
6. Produces a dependency-aware task graph.
7. Dynamically assembles leadership, specialist, and evaluator agents.
8. Creates the proposed implementation and validation plan.
9. Publishes linked summaries to available systems.
10. Enters `AWAITING_CAPTAIN_APPROVAL` and stops.

### Phase 3: Approval

The canonical approval record consists of:

- an explicit Captain decision attached to the GitHub issue or PR; and
- the matching approved plan ID, content digest, and repository state.

Slack and Linear may record approval intent, but cannot independently authorize
Cursor execution. Conflicting, stale, ambiguous, or identity-unverified approval
events move the run to `BLOCKED_APPROVAL`.

### Phase 4: Dispatch

After approval, the First Mate:

1. Creates or confirms the GitHub issue.
2. Creates the rollback reference.
3. Creates a feature branch and isolated worktree.
4. Creates Linear workstream issues and dependency links.
5. Builds the signed Cursor work packet.
6. Dispatches or resumes only cloud agent
   `bc-05d4594d-fac7-4378-b595-c20e3c006044`.
7. Verifies the returned agent identity before accepting a checkpoint.
8. Moves the run to `IN_PROGRESS`.

If the agent identity does not match, NorthStar stops in
`BLOCKED_AGENT_IDENTITY`. A previous release agent must never be resumed or
silently substituted for the M21 integration runtime.

### Phase 5: Execution and evidence

Cursor receives only the approved work packet and implements the approved task
graph. It writes evidence under `.agent/evidence/<run_id>/`, updates meaningful
checkpoints, and stops when scope, budget, validation, or permission boundaries
are reached.

NorthStar publishes only these Slack transitions:

- work received
- plan awaiting approval
- execution started
- blocked or budget stopped
- review ready
- completed

Linear and GitHub receive durable status updates. Internal reasoning and noisy
per-command updates are not copied between systems.

### Phase 6: Review and closeout

1. Run the selected evaluator and adversarial-review agents.
2. Complete required static, unit, integration, end-to-end, security,
   accessibility, build, deployment, and rollback validation.
3. Open or update the GitHub pull request.
4. Link the PR and evidence to Linear workstreams.
5. Enter `AWAITING_MERGE` and stop for Captain approval.
6. After merge, reconcile GitHub and Linear state.
7. Publish the Slack completion summary.
8. Record execution telemetry and Experience artifacts.
9. Send any Skill improvement through the existing Captain-gated learning flow.

## State model

Normal states:

`RECEIVED -> RECONCILING -> PLAN_PROPOSED -> AWAITING_CAPTAIN_APPROVAL -> DISPATCHED -> IN_PROGRESS -> VALIDATING -> REVIEW_READY -> AWAITING_MERGE -> COMPLETED`

Exception states:

- `BLOCKED_CONNECTION`
- `BLOCKED_APPROVAL`
- `BLOCKED_AGENT_IDENTITY`
- `BLOCKED_SCOPE`
- `BUDGET_STOPPED`
- `VALIDATION_FAILED`
- `CANCELLED`
- `SUPERSEDED`

Every state transition is append-only and includes the actor, origin, timestamp,
previous state, next state, event digest, plan digest, and correlation IDs.

## Normalized event contract

```json
{
  "event_id": "provider-event-id",
  "provider": "slack|linear|github|cursor",
  "event_type": "objective|work_item_changed|pull_request_changed|checkpoint|approval",
  "occurred_at": "RFC3339",
  "actor": {
    "provider_id": "provider-actor-id",
    "verified_role": "captain|first_mate|agent|collaborator"
  },
  "product": {
    "name": "NorthStar",
    "legacy_alias_received": null
  },
  "project": {
    "repository": "loganware05/captains-compass-cursor"
  },
  "references": {
    "slack_thread": null,
    "linear_issue": null,
    "github_issue": null,
    "github_pull_request": null,
    "cursor_agent": "bc-05d4594d-fac7-4378-b595-c20e3c006044"
  },
  "payload_digest": "sha256",
  "idempotency_key": "sha256"
}
```

## Connector interface

Each provider adapter implements:

- `healthcheck()`
- `normalize_event(raw_event)`
- `read_context(reference)`
- `verify_identity(actor)`
- `deduplicate(event_id, idempotency_key)`
- `create_or_update_work_item(run)`
- `publish_transition(run, transition)`
- `link_artifacts(run)`
- `reconcile(run)`

## Proposed implementation surface

- `orchestrator/branding.py`
- `orchestrator/integrations/contracts.py`
- `orchestrator/integrations/events.py`
- `orchestrator/integrations/state_machine.py`
- `orchestrator/integrations/reconcile.py`
- `orchestrator/integrations/adapters/github.py`
- `orchestrator/integrations/adapters/linear.py`
- `orchestrator/integrations/adapters/slack.py`
- `orchestrator/integrations/adapters/cursor.py`
- `scripts/run-northstar-routine.sh`
- `scripts/reconcile-northstar-run.sh`
- `.cursor/skills/northstar-connected-routine/SKILL.md`
- `docs/integrations/slack.md`
- updates to active templates, agent manifests, integration docs, security docs,
  `UPGRADING.md`, `DECISIONS.md`, `PROGRESS.md`, `TESTING.md`, and changelog
- recorded fixtures for all four adapters with no live credentials in CI

## Delivery workstreams

### M21A: Identity, contracts, and state

- NorthStar branding registry and legacy aliases
- normalized event and work-packet schemas
- idempotency and correlation store
- state-transition validator
- fixture adapters

### M21B: GitHub and Cursor bridge

- authoritative GitHub adapter
- plan digest and approval verification
- cloud-agent work packet
- agent identity enforcement for
  `bc-05d4594d-fac7-4378-b595-c20e3c006044`
- checkpoint and evidence ingestion

### M21C: Linear ledger

- parent initiative and child workstreams
- dependencies, statuses, owners, acceptance criteria, and PR links
- retry and out-of-order reconciliation
- GitHub issue fallback

### M21D: Slack edge

- allowlisted channel intake
- `@NorthStar` mention requirement
- temporary legacy mention compatibility
- threaded transition notifications
- identity-aware approval intent without independent execution authority

### M21E: Hardening and release

- adversarial event and prompt-injection fixtures
- replay, stale-event, redaction, and connector-loss tests
- existing-installation and rollback tests
- sandbox end-to-end smoke
- documentation and release closeout

## Safety and fallback rules

- Connector scopes must be least privilege and project allowlisted.
- Secrets never enter prompts, logs, Slack, Linear, GitHub, evidence, or fixtures.
- Captain identity is verified per provider before recording approval intent.
- No automatic merge, release, live Skill install, permission change, or
  destructive production action.
- Missing Linear falls back to GitHub issues.
- Missing Slack suppresses conversation notifications without blocking GitHub
  and Linear status.
- Missing Cursor produces a launch-ready work packet and stops.
- Missing GitHub stops the entire engineering routine.
- Conflicting system state is reconciled from GitHub and the approved plan.

## Acceptance criteria

- [x] All new human-facing output uses NorthStar.
- [x] Legacy product names resolve to the same NorthStar project and run.
- [x] Rebranding cannot duplicate Slack threads, Linear issues, GitHub work, or Cursor runs.
- [x] Existing installations and historical identifiers continue to work.
- [x] One objective creates exactly one correlated run.
- [x] Duplicate and replayed events have no duplicate side effects.
- [x] No Cursor execution occurs before canonical Captain approval.
- [x] Only cloud agent `bc-05d4594d-fac7-4378-b595-c20e3c006044` is accepted for M21 integration checkpoints.
- [x] Cursor can resume entirely from the approved work packet.
- [x] GitHub remains the engineering and approval source of truth.
- [x] Linear dependencies and statuses reconcile after retries and out-of-order events.
- [x] Slack messages are threaded and transition-only.
- [x] Connector loss follows the documented fallback policy.
- [x] Unit tests cover branding, normalization, identity, deduplication, transitions, approvals, retries, and redaction.
- [x] Integration tests use recorded fixtures for all four providers.
- [x] An end-to-end fixture run reaches `REVIEW_READY` with complete evidence.
- [x] Security and adversarial review pass.
- [x] `./scripts/doctor.sh` and `./tests/run.sh` pass.
- [x] Upgrade, rollback, testing, decision, progress, and release documentation are updated.

## Recommended defaults awaiting approval

1. Use an allowlisted Slack channel and explicit `@NorthStar` mention.
2. Use one Linear M21 parent issue, child workstreams, and a `northstar` label.
3. Require explicit Captain dispatch to the configured Cursor agent after plan approval.
4. Use a GitHub approval record plus matching plan digest as canonical approval.
5. Send Slack notifications only for meaningful state transitions.
6. Retain the repository slug, `.agent/`, `.cursor/`, existing Skill IDs, and
   historical machine identifiers during M21.
7. Use an autonomy budget of eight iterations and three failed validation cycles.
8. Target the next minor release after `v1.24.0`.

## Non-goals

- Renaming or transferring the GitHub repository during M21
- Rewriting historical artifacts
- Automatic merging or releasing
- Automatic live Skill installation
- Replacing the Captain approval gate with Slack or Linear reactions
- Allowing arbitrary Cursor agents to join an active run
- Closing stale issue #50 or merging sandbox PR #40 as part of product scope

## Autonomy budget (proposed; activates on approval)

| Limit | Value |
|---|---|
| Maximum iterations | 8 |
| Maximum failed validation cycles | 3 |
| Stop on scope change | true |
| Stop on destructive operation | true |
| Stop on unresolved security high | true |

Ledger path after approval: `.agent/budgets/m21-northstar-connected-operations.md`

## Capability planning appendix (machine-generated; proposals only)

Generated 2026-09-08 via `./scripts/capability-plan.sh --plan-id m21-northstar-connected-operations`.

**Authoritative delivery order remains M21A → M21E above.** The generic
discovery → architecture → implementation → validation → documentation graph
below is supporting context only.

### Required Capabilities

- implementation-plan-authoring
- approval-gate-enforcement
- scope-definition
- rollback-planning
- github-issue-create
- github-pr-create
- pr-description-assembly

**Domains detected:** plan, github

### Reusable Capabilities Found (top)

| Skill | Score | Notes |
|---|---:|---|
| `implementation-planning` | 0.5571 | capability_overlap=0.2571 |
| `github-integration` | 0.4286 | lifecycle_stage=0.15 |
| `pull-request-preparation` | 0.3643 | lifecycle_stage=0.15 |
| `linear-integration` | 0.3 | lifecycle_stage=0.15 |
| `security-review` | 0.3 | lifecycle_stage=0.15 |
| `testing-validation` | 0.3 | lifecycle_stage=0.15 |
| `autonomy-budget` | 0.3 | lifecycle_stage=0.15 |
| `capability-planning` | 0.3 | lifecycle_stage=0.15 |
| `worktree-orchestration` | 0.3 | lifecycle_stage=0.15 |

Capability gaps: none detected for inferred requirements.

Artifacts (gitignored): `.agent/plans/m21-northstar-connected-operations/{resolve,task-graph,manifests}.json`

## Approval record

| Captain | Decision | Date |
|---|---|---|
| Captain | **APPROVED** — implement `m21-northstar-connected-operations` | 2026-09-08 |

Approved plan digest baseline: repository state at approval branch
`cursor/m21-northstar-connected-operations-6044` continuing from plan docs at
`5398b55` / main `13b5879`.
