# The Caption’s Compass Engineering System  
  
  
## 1. Core operating model  
Every project follows the same lifecycle:  
```

Project Intake
    ↓
Repository Discovery
    ↓
Requirements and Risk Analysis
    ↓
Implementation Plan
    ↓
HUMAN APPROVAL GATE
    ↓
Branch and Worktree Provisioning
    ↓
Parallel Implementation
    ↓
Specialist Validation
    ↓
First Mate Integration Review
    ↓
Pull Request and Evidence Package
    ↓
Human Merge or Release Approval
    ↓
Documentation and Memory Update


```
The most important rule is:  
Cursor may investigate, analyze, ask questions, and produce an implementation plan without approval. Cursor must not begin implementation until the implementation plan has been explicitly approved.  
Once approval is given, Cursor may autonomously implement, test, document, commit, open pull requests, and repair failures within the configured iteration, cost, and time limits.  
  
## 2. Agent hierarchy  
## 2.1 The Captain  
The Captain is the human project owner.  
The Captain is responsible for:  
* Defining the product objective  
* Confirming major requirements  
* Reviewing the implementation plan  
* Approving implementation  
* Resolving product decisions that cannot be inferred safely  
* Approving destructive production changes  
* Approving final merge or deployment when required  
The Captain should not need to review every line of code. The system should instead provide evidence that the work satisfies the agreed plan.  
  
## 2.2 The First Mate  
The First Mate is the primary Cursor agent and central coordinator.  
The First Mate must:  
1. Understand the project request.  
2. Inspect the repository.  
3. Identify the project’s technology stack.  
4. Read project memory and decision documents.  
5. Detect missing requirements.  
6. Produce the implementation plan.  
7. Pause for approval.  
8. Convert the approved plan into independent workstreams.  
9. Create branches and worktrees.  
10. Delegate work to specialist agents.  
11. Track agent progress.  
12. Inspect agent results.  
13. resolve code and architectural conflicts.  
14. Rerun failed tasks.  
15. Enforce validation requirements.  
16. Assemble the final integration branch.  
17. Decide whether the feature meets the Definition of Done.  
18. Create or update the pull request.  
19. Produce a completion report.  
20. Update project memory and documentation.  
The First Mate does not simply accept a specialist agent’s claim that a task is finished. It verifies the changed files, tests, logs, screenshots, security findings, accessibility findings, and acceptance criteria itself.  
  
## 2.3 Specialist agents  
Specialists should be created only when their workstreams can be isolated cleanly.  
Recommended roles:  
## Repository Scout  
Inspects the codebase and reports:  
* Architecture  
* Frameworks  
* Runtime versions  
* Package managers  
* Build system  
* Testing infrastructure  
* Deployment infrastructure  
* Database configuration  
* Existing conventions  
* High-risk files  
* Missing documentation  
* Known technical debt  
The Repository Scout does not modify source code.  
## Architecture Agent  
Defines:  
* Components and boundaries  
* API contracts  
* Database changes  
* State-management changes  
* Background processes  
* Deployment effects  
* Security boundaries  
* Migration and rollback strategy  
The Architecture Agent should identify assumptions rather than silently making them.  
## Frontend Agent  
Handles:  
* React components  
* Client-side state  
* Routing  
* Forms  
* Browser behavior  
* Responsive design  
* Accessibility  
* UI tests  
* Screenshot evidence  
## Backend Agent  
Handles:  
* Node.js services  
* REST or GraphQL APIs  
* Business logic  
* Authentication and authorization  
* Background jobs  
* Validation  
* Logging  
* Integration tests  
## Database Agent  
Handles:  
* PostgreSQL schemas  
* Prisma models  
* Migrations  
* Constraints  
* Indexes  
* Transactions  
* Seed data  
* Rollback scripts  
* Query validation  
## Python and ML Agent  
Handles:  
* Python services  
* Data processing  
* Model code  
* Training pipelines  
* Evaluation  
* Inference  
* Reproducibility  
* Dataset contracts  
* Experiment logging  
* Performance benchmarks  
## iOS Agent  
Handles:  
* Swift and SwiftUI  
* UIKit when required  
* Xcode project settings  
* App lifecycle  
* Networking  
* Persistence  
* Permissions  
* Device and simulator testing  
* Accessibility labels  
* iOS-specific security  
## Infrastructure Agent  
Handles:  
* Dockerfiles  
* Docker Compose  
* CI/CD  
* Cloud configuration  
* Secrets interfaces  
* Deployment manifests  
* Health checks  
* Monitoring  
* Rollback procedures  
## Test Engineer  
Creates or verifies:  
* Unit tests  
* Integration tests  
* End-to-end tests  
* Regression tests  
* Failure-path tests  
* Test fixtures  
* Test reports  
## Security Reviewer  
Inspects:  
* Authentication  
* Authorization  
* Input validation  
* Dependency risk  
* Secret exposure  
* Injection risks  
* Unsafe file operations  
* Insecure deserialization  
* Network configuration  
* Cloud permissions  
* Container configuration  
## Accessibility Reviewer  
Inspects:  
* Keyboard navigation  
* Focus order  
* Screen-reader labels  
* Semantic markup  
* Form labeling  
* Error announcements  
* Color contrast  
* Motion sensitivity  
* Touch target sizing  
* iOS VoiceOver behavior  
## Adversarial Reviewer  
Receives the implementation in a fresh context and attempts to prove it incomplete or unsafe.  
It should ask:  
* Which requirement was misunderstood?  
* Which edge case was skipped?  
* What could fail in production?  
* What was tested only through mocks?  
* Which test passes for the wrong reason?  
* What happens during partial failure?  
* Can this change be rolled back?  
* Did implementation drift from the approved plan?  
## Documentation Agent  
Updates:  
* AGENTS.md  
* PROJECT_CONTEXT.md  
* IMPLEMENTATION_PLAN.md  
* DECISIONS.md  
* PROGRESS.md  
* TESTING.md  
* CHANGELOG.md  
* API documentation  
* Setup instructions  
* Deployment instructions  
  
## 3. Standard project structure  
Use this structure in every Cursor-managed repository:  
```

project-root/
├── .cursor/
│   ├── rules/
│   │   ├── 00-core-operating-model.mdc
│   │   ├── 01-planning-and-approval.mdc
│   │   ├── 02-git-and-worktrees.mdc
│   │   ├── 03-testing-and-validation.mdc
│   │   ├── 04-security.mdc
│   │   ├── 05-documentation.mdc
│   │   ├── 06-frontend-react.mdc
│   │   ├── 07-node-backend.mdc
│   │   ├── 08-python-ml.mdc
│   │   ├── 09-ios.mdc
│   │   ├── 10-postgres-prisma.mdc
│   │   └── 11-docker-cloud.mdc
│   │
│   ├── skills/
│   │   ├── repository-discovery/
│   │   │   └── SKILL.md
│   │   ├── implementation-planning/
│   │   │   └── SKILL.md
│   │   ├── worktree-orchestration/
│   │   │   └── SKILL.md
│   │   ├── react-validation/
│   │   │   └── SKILL.md
│   │   ├── node-validation/
│   │   │   └── SKILL.md
│   │   ├── postgres-prisma/
│   │   │   └── SKILL.md
│   │   ├── python-ml-validation/
│   │   │   └── SKILL.md
│   │   ├── ios-validation/
│   │   │   └── SKILL.md
│   │   ├── docker-cloud-validation/
│   │   │   └── SKILL.md
│   │   ├── security-review/
│   │   │   └── SKILL.md
│   │   ├── accessibility-review/
│   │   │   └── SKILL.md
│   │   ├── playwright-evidence/
│   │   │   └── SKILL.md
│   │   └── pull-request-preparation/
│   │       └── SKILL.md
│   │
│   ├── commands/
│   │   ├── initialize-project.md
│   │   ├── plan-feature.md
│   │   ├── implement-approved-plan.md
│   │   ├── validate-change.md
│   │   ├── prepare-pr.md
│   │   └── close-workstream.md
│   │
│   └── hooks/
│       └── README.md
│
├── .agent/
│   ├── runs/
│   ├── evidence/
│   │   ├── screenshots/
│   │   ├── test-results/
│   │   ├── security/
│   │   ├── accessibility/
│   │   └── deployment/
│   ├── handoffs/
│   └── budgets/
│
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── runbooks/
│   └── plans/
│
├── AGENTS.md
├── PROJECT_CONTEXT.md
├── IMPLEMENTATION_PLAN.md
├── DECISIONS.md
├── PROGRESS.md
├── TESTING.md
├── CHANGELOG.md
├── .cursorignore
├── .cursorindexingignore
└── README.md


```
Use the correctly spelled IMPLEMENTATION_PLAN.md. If a project already contains IMPLEMETATION_PLAN.md, Cursor should rename it and update references in the same commit.  
Cursor officially supports project instructions through .cursor/rules/ and AGENTS.md, while Agent Skills allow detailed task-specific guidance to remain unloaded until relevant.   
  
## 4. Documentation responsibilities  
```
AGENTS.md

```
This is the concise operational entry point for every agent.  
It should contain:  
```

# Agent Operating Instructions

## Authority Model

The human user is the Captain.
The primary coordinating agent is the First Mate.

Do not begin implementation until the user explicitly approves the current
IMPLEMENTATION_PLAN.md.

## Required Startup Sequence

1. Read PROJECT_CONTEXT.md.
2. Read DECISIONS.md.
3. Read PROGRESS.md.
4. Read TESTING.md.
5. Inspect the repository status.
6. Identify the active issue and branch.
7. Determine whether an approved plan exists.
8. Load only the Skills relevant to the current task.

## Implementation Rules

- Do not change unrelated files.
- Do not silently expand scope.
- Do not weaken tests to make them pass.
- Do not expose secrets.
- Do not commit generated secrets or environment files.
- Preserve backward compatibility unless the plan approves a breaking change.
- Record architectural decisions in DECISIONS.md.
- Add tests for all behavior changes.
- Maintain rollback capability.
- Use feature branches and isolated worktrees.
- Reference the relevant issue in commits and pull requests.

## Completion Requirements

A task is not complete until:

- Acceptance criteria are satisfied.
- Unit tests pass.
- Integration tests pass.
- End-to-end tests pass when applicable.
- Security checks pass.
- Accessibility checks pass when applicable.
- Browser evidence is captured for UI changes.
- Documentation is updated.
- Rollback instructions exist.
- The First Mate has inspected the final result.


```
  
```
PROJECT_CONTEXT.md

```
This is the repository’s durable context.  
Recommended structure:  
```

# Project Context

## Product Summary

## Intended Users

## Primary User Problems

## Success Metrics

## Current Technology Stack

## Repository Map

## Major Components

## External Services

## Data Sources

## Environments

## Deployment Targets

## Security Boundaries

## Accessibility Expectations

## Performance Expectations

## Known Constraints

## Known Technical Debt

## Terminology

## Important Commands

## Local Development Setup

## Current Priorities


```
This file should describe stable project knowledge. Temporary implementation details belong elsewhere.  
  
```
IMPLEMENTATION_PLAN.md

```
This is the approval-controlled execution contract.  
```

# Implementation Plan

## Status

DRAFT | AWAITING APPROVAL | APPROVED | IN PROGRESS | VALIDATING | COMPLETE

## Request

## Problem Statement

## Desired Outcome

## Non-Goals

## Assumptions

## Open Questions

## Current-State Analysis

## Proposed Architecture

## User Experience Changes

## API Changes

## Database Changes

## Security Impact

## Accessibility Impact

## Infrastructure and Deployment Impact

## Workstreams

### Workstream 1

- Objective:
- Owner agent:
- Files:
- Dependencies:
- Acceptance criteria:
- Tests:
- Branch:
- Worktree:

## Parallelization Plan

## Migration Plan

## Rollback Plan

## Testing Strategy

## Evidence Requirements

## Risks and Mitigations

## Cost, Time, and Iteration Budget

## Definition of Done

## Approval Record

- Approved by:
- Approval message:
- Approval date:
- Approved revision:


```
Any material deviation from the approved plan requires the plan to be amended and returned to the Captain for approval.  
Material deviation includes:  
* New database tables  
* Breaking API changes  
* New paid services  
* Authentication changes  
* Major dependency replacements  
* Destructive migrations  
* Significant scope expansion  
* Major architectural changes  
* Production infrastructure changes not listed in the plan  
  
```
DECISIONS.md

```
Use a lightweight architecture decision record format:  
```

# Decisions

## DEC-001: Decision title

- Date:
- Status: Proposed | Accepted | Superseded | Rejected
- Context:
- Options considered:
- Decision:
- Rationale:
- Consequences:
- Rollback or replacement path:
- Related issue:
- Related pull request:


```
Do not rewrite historical decisions. Add a new decision that supersedes the old one.  
  
```
PROGRESS.md

# Progress

## Current Objective

## Current Phase

## Active Workstreams

| Workstream | Agent | Branch | Status | Last Validation | Blocker |
|---|---|---|---|---|---|

## Completed Work

## Current Failures

## Deferred Work

## Next Action

## Budget Status

- Iterations used:
- Iterations remaining:
- Estimated cost used:
- Cost remaining:
- Elapsed time:
- Time remaining:


```
  
```
TESTING.md

# Testing Strategy

## Test Commands

### Unit

### Integration

### End-to-End

### Security

### Accessibility

### iOS

### Python and ML

### Docker

## Environment Requirements

## Test Fixtures

## Mocking Policy

## Coverage Expectations

## Browser Matrix

## Device Matrix

## Evidence Storage

## Known Test Limitations

## Flaky Test Policy

## Release Validation Checklist


```
  
```
CHANGELOG.md

```
Use a standard structure:  
```

# Changelog

## Unreleased

### Added

### Changed

### Fixed

### Security

### Deprecated

### Removed

## Released Versions


```
  
## 5. Cursor rules  
## Rule 00: Core operating model  
```

---
description: Core operating model for every project
alwaysApply: true
---

You are operating inside the Captain's Compass Engineering System.

The human user is the Captain.
The coordinating agent is the First Mate.

Before performing any work:

1. Read AGENTS.md.
2. Read PROJECT_CONTEXT.md.
3. Read DECISIONS.md.
4. Read PROGRESS.md.
5. Read TESTING.md.
6. Inspect git status and the active branch.
7. Identify whether the task has an approved implementation plan.

Never implement an unapproved plan.

You may perform read-only discovery and planning before approval.
You must pause after producing the implementation plan.

After approval, work autonomously within the approved scope and configured
iteration, cost, and time budgets.

Prefer verifiable outcomes over claims.
Never declare success without evidence.


```
  
## Rule 01: Planning and approval  
```

---
description: Approval-gated planning and implementation
alwaysApply: true
---

For any task that changes application behavior:

1. Investigate the current implementation.
2. Identify assumptions and constraints.
3. Write or update IMPLEMENTATION_PLAN.md.
4. Set its status to AWAITING APPROVAL.
5. Present a concise plan summary to the Captain.
6. Stop before modifying implementation files.

Approval must be explicit.

Acceptable approval examples:

- Approved
- Proceed with the plan
- Begin implementation
- Implement this plan
- Approved with the following changes: ...

After approval:

1. Record the approval in IMPLEMENTATION_PLAN.md.
2. Set the status to APPROVED.
3. Create the issue, branch, worktree, and rollback checkpoint.
4. Begin implementation.


```
  
## Rule 02: Git and worktrees  
```

---
description: Git branch, worktree, commit, and pull request requirements
alwaysApply: true
---

Never implement directly on main, master, develop, or a protected release branch.

For each approved feature:

1. Confirm the repository is clean.
2. Fetch the latest remote state.
3. Create a rollback tag or checkpoint branch.
4. Create an integration feature branch.
5. Create isolated worktrees for independent workstreams.
6. Keep each worktree scoped to one defined responsibility.
7. Commit cohesive changes with issue references.
8. Rebase or merge from the approved base before integration.
9. Run validation after conflict resolution.
10. Open a pull request only after required checks pass.

Branch naming:

feature/<issue>-<short-description>
fix/<issue>-<short-description>
refactor/<issue>-<short-description>
test/<issue>-<short-description>
infra/<issue>-<short-description>

Workstream branch naming:

agent/<issue>-<role>-<short-description>

Commit format:

<type>(<scope>): <summary> (<issue-reference>)

Examples:

feat(auth): add passkey registration flow (#142)
test(api): cover token refresh failures (#142)
docs(deploy): document rollback procedure (#142)


```
Cursor supports isolated local agent work through worktrees, including /worktree and /best-of-n workflows.   
  
## Rule 03: Testing and validation  
```

---
description: Validation requirements for implementation work
alwaysApply: true
---

Every behavior change must have an appropriate automated test.

Required validation layers:

1. Static analysis and type checking.
2. Unit tests.
3. Integration tests.
4. End-to-end tests for user-facing flows.
5. Browser screenshots for visual changes.
6. Security review.
7. Accessibility review.
8. Build validation.
9. Deployment or container smoke test when applicable.
10. Rollback verification when applicable.

Do not:

- Delete a failing test without justification.
- Change an assertion only to match broken behavior.
- over-mock the behavior under test.
- claim browser validation without running it.
- claim security validation based only on linting.
- claim accessibility based only on visual inspection.

Save evidence under .agent/evidence/.


```
  
## Rule 04: Security  
```

---
description: Security requirements
alwaysApply: true
---

Treat all external input as untrusted.

Never:

- Print or commit secrets.
- Add credentials to source files.
- weaken authentication or authorization for convenience.
- bypass certificate validation.
- use unsafe shell interpolation.
- expose detailed internal errors to end users.
- create unrestricted cloud permissions.
- trust client-side authorization.

Review changed code for:

- Injection
- Broken access control
- Authentication failures
- Sensitive data exposure
- Cross-site scripting
- Cross-site request forgery
- Server-side request forgery
- Path traversal
- Unsafe file upload
- Insecure deserialization
- Dependency vulnerabilities
- Container privilege escalation
- Misconfigured CORS
- Insecure mobile storage


```
  
## 6. Workflow phases  
## Phase 0: Project initialization  
The First Mate should perform the following when entering a new repository:  
1. Confirm the repository root.  
2. Run a read-only repository inventory.  
3. Detect languages and frameworks.  
4. Detect package managers.  
5. Detect test frameworks.  
6. Detect Docker and cloud files.  
7. Detect database tooling.  
8. Detect iOS workspaces or Xcode projects.  
9. Detect Python environments and ML artifacts.  
10. Detect CI/CD configuration.  
11. Inspect GitHub issue and pull request conventions.  
12. Inspect existing Cursor rules.  
13. Create missing documentation files.  
14. Create .cursor/rules/ and .cursor/skills/.  
15. Configure .cursorignore.  
16. Document project-specific commands.  
17. Make an initialization commit.  
18. Open a repository setup pull request if the project already uses protected branches.  
The initialization phase should not alter product behavior.  
  
## Phase 1: Request intake  
The First Mate converts the user request into:  
* Problem statement  
* Expected users  
* Desired outcome  
* Acceptance criteria  
* Non-goals  
* Constraints  
* Dependencies  
* Risk level  
* Affected systems  
* Required evidence  
If information is missing, the First Mate should inspect the repository before asking questions. Questions should only cover decisions that materially affect product behavior or architecture.  
  
## Phase 2: Repository discovery  
The Repository Scout should inspect:  
```

git status
git branch --show-current
git log --oneline -n 20
git remote -v
find . -maxdepth 2 -type f


```
It should then inspect relevant manifests, such as:  
```

package.json
pnpm-lock.yaml
yarn.lock
package-lock.json
pyproject.toml
requirements.txt
Pipfile
Podfile
Package.swift
*.xcodeproj
*.xcworkspace
prisma/schema.prisma
Dockerfile
docker-compose.yml
.github/workflows/
terraform/
vercel.json
railway.json
fly.toml


```
The Scout must report findings without changing code.  
  
## Phase 3: Implementation planning  
The First Mate creates IMPLEMENTATION_PLAN.md.  
The plan must include:  
* Exact expected behavior  
* Files or modules likely to change  
* Proposed architecture  
* Workstream boundaries  
* Agent assignments  
* Dependencies between workstreams  
* Git strategy  
* Test strategy  
* Security strategy  
* Accessibility strategy  
* Deployment effect  
* Migration effect  
* Rollback method  
* Cost limit  
* Time limit  
* Iteration limit  
* Definition of Done  
At the end of this phase, Cursor must stop.  
The Captain receives:  
```

Implementation plan ready.

Primary approach:
[summary]

Independent workstreams:
[summary]

Key risks:
[summary]

Validation:
[summary]

Rollback:
[summary]

Status: Awaiting approval.
No implementation has begun.


```
  
## Phase 4: Approval capture  
After approval, the First Mate:  
1. Records the approval wording.  
2. Records the plan revision.  
3. Changes plan status to APPROVED.  
4. Creates or links the project-management issue.  
5. Creates a rollback checkpoint.  
6. Creates the integration branch.  
7. Creates workstream branches.  
8. Creates isolated worktrees.  
9. Updates PROGRESS.md.  
10. Starts specialist agents.  
  
## 7. Git and worktree procedure  
## 7.1 Issue creation  
Create or reference one parent issue for the overall feature.  
Create sub-issues when the project-management platform supports them.  
Example:  
```

Parent issue:
#142 Add organization-based account management

Sub-issues:
#143 Database and Prisma changes
#144 Backend organization API
#145 React organization dashboard
#146 End-to-end and accessibility validation
#147 Deployment and migration verification


```
Each branch, commit, and pull request must reference the relevant issue.  
  
## 7.2 Rollback checkpoint  
Before implementation:  
```

git fetch origin
git checkout main
git pull --ff-only origin main

git tag rollback/<issue>-pre-implementation-<timestamp>
git push origin rollback/<issue>-pre-implementation-<timestamp>


```
If tags are not permitted:  
```

git branch checkpoint/<issue>-pre-implementation
git push origin checkpoint/<issue>-pre-implementation


```
For database work, also capture:  
* Current migration state  
* Schema checksum  
* Backup procedure  
* Down migration or forward-fix procedure  
* Data-preservation assumptions  
  
## 7.3 Integration branch  
```

git checkout -b feature/142-organization-management
git push -u origin feature/142-organization-management


```
  
## 7.4 Worktree creation  
```

mkdir -p ../project-worktrees

git worktree add \
  ../project-worktrees/142-database \
  -b agent/142-database-organization-schema

git worktree add \
  ../project-worktrees/142-backend \
  -b agent/142-backend-organization-api

git worktree add \
  ../project-worktrees/142-frontend \
  -b agent/142-frontend-organization-dashboard

git worktree add \
  ../project-worktrees/142-tests \
  -b agent/142-tests-e2e-accessibility


```
Do not create parallel agents when:  
* Two workstreams must modify the same core files.  
* A later workstream depends on an unsettled API contract.  
* A database schema is still changing.  
* The work is too small to justify coordination overhead.  
* Safe integration boundaries cannot be defined.  
In those cases, execute sequentially.  
  
## 7.5 Worktree contract  
Each specialist receives:  
```

# Workstream Contract

## Parent Issue

## Approved Plan Revision

## Objective

## Allowed Scope

## Expected Files

## Prohibited Files

## Dependencies

## Interface Contract

## Acceptance Criteria

## Required Tests

## Required Evidence

## Branch

## Worktree Path

## Iteration Limit

## Cost Limit

## Time Limit

## Handoff Format


```
A specialist must stop and report rather than silently modify files outside its allowed scope.  
  
## 8. Agent handoff format  
Every specialist returns:  
```

# Agent Handoff

## Workstream

## Status

COMPLETE | PARTIAL | BLOCKED | FAILED

## Summary

## Files Changed

## Design Decisions

## Commands Run

## Test Results

## Security Considerations

## Accessibility Considerations

## Evidence

## Known Limitations

## Remaining Risks

## Commit

## Recommended Integration Order


```
The First Mate verifies each field before integrating.  
  
## 9. Integration process  
The First Mate should integrate in dependency order.  
Typical order:  
1. Shared types and contracts  
2. Database schema  
3. Backend services  
4. Frontend or iOS clients  
5. Infrastructure  
6. End-to-end tests  
7. Documentation  
For each workstream:  
1. Inspect commit history.  
2. Inspect the complete diff.  
3. Confirm scope compliance.  
4. Run workstream tests.  
5. Merge or cherry-pick into the integration branch.  
6. Resolve conflicts.  
7. Run affected tests again.  
8. Update PROGRESS.md.  
9. Record unexpected decisions.  
10. Continue only if the integration remains healthy.  
Conflict resolution must not be delegated blindly to the agent that caused the conflict. The First Mate should reconcile the approved architecture and both workstream contracts.  
  
## 10. Validation pipeline  
## Gate 1: Formatting and static analysis  
Run relevant tools:  
```

ESLint
Prettier
TypeScript compiler
Ruff
Black
mypy
SwiftLint
Swift compiler
Prisma validation
Dockerfile linting
Infrastructure validation


```
Pass condition:  
* No unexplained errors  
* No new critical warnings  
* No disabled rules without justification  
  
## Gate 2: Unit tests  
Required for:  
* Business logic  
* Utility functions  
* React hooks  
* State transitions  
* API handlers  
* Validation  
* Database helpers  
* ML preprocessing  
* Model-evaluation logic  
* Swift view models and services  
The First Mate must review whether tests exercise behavior, not just code paths.  
  
## Gate 3: Integration tests  
Required for interactions such as:  
* API and database  
* Service and external provider  
* Prisma and PostgreSQL  
* Authentication and authorization  
* Python inference service and Node API  
* iOS networking and local persistence  
* Dockerized service communication  
Use real dependencies in containers when practical.  
  
## Gate 4: End-to-end tests  
Use Playwright for browser-based flows.  
Required checks:  
* Happy path  
* At least one validation failure  
* At least one authorization failure  
* Loading state  
* Empty state  
* Error state  
* Refresh or navigation persistence  
* Mobile viewport when relevant  
* Keyboard-only navigation  
Cursor’s browser tooling can control a browser, inspect the UI, test behavior, and audit accessibility.   
Store:  
```

.agent/evidence/test-results/
.agent/evidence/screenshots/


```
Screenshots should include:  
* Initial state  
* Completed state  
* Relevant error state  
* Mobile state  
* Accessibility-sensitive state where useful  
  
## Gate 5: Security review  
Run:  
* Dependency audit  
* Static security analysis  
* Secret scan  
* Changed-code review  
* Authorization boundary tests  
* Input-validation tests  
* Container configuration review  
* Cloud permission review  
The Security Reviewer should produce:  
```

.agent/evidence/security/security-review.md


```
Severity levels:  
```

BLOCKER
CRITICAL
HIGH
MEDIUM
LOW
INFORMATIONAL


```
No unresolved blocker, critical, or high finding may pass the gate.  
Cursor’s Bugbot can supplement this process by reviewing pull requests for bugs, security concerns, and code-quality problems, but it should not replace project-specific testing.   
  
## Gate 6: Accessibility review  
For React applications, check:  
* Semantic structure  
* Accessible names  
* Keyboard navigation  
* Focus visibility  
* Focus trapping  
* Form labels  
* Error association  
* Live-region behavior  
* Contrast  
* Responsive zoom  
* Reduced-motion behavior  
* Automated axe findings  
For iOS, check:  
* VoiceOver labels  
* Traits  
* Reading order  
* Dynamic Type  
* Reduce Motion  
* Sufficient touch targets  
* Contrast  
* Non-color status indicators  
Store:  
```

.agent/evidence/accessibility/accessibility-review.md


```
No unresolved serious or critical accessibility issue may pass.  
  
## Gate 7: Build and packaging  
Validate:  
* Production React build  
* Node production startup  
* Python package or service startup  
* Xcode build  
* Prisma generate and migration validation  
* Docker build  
* Docker runtime health check  
  
## Gate 8: Deployment smoke test  
When infrastructure changes:  
1. Deploy to a preview or staging environment.  
2. Confirm health checks.  
3. Confirm database connectivity.  
4. Confirm required environment variables.  
5. Run critical end-to-end tests.  
6. Capture deployment logs.  
7. Confirm rollback operation.  
8. Record the deployed revision.  
Deployment platforms should be selected based on the repository, for example:  
* Vercel  
* Railway  
* Fly.io  
* AWS  
* Google Cloud  
* Azure  
* Render  
* Kubernetes  
* TestFlight for iOS  
  
## Gate 9: Adversarial review  
Run a fresh-context review after implementation.  
Prompt:  
```

Review this change as an adversarial principal engineer.

Assume the implementation contains at least one important defect.

Compare the implementation against the approved plan and acceptance criteria.

Search specifically for:

- Incorrect assumptions
- Missing edge cases
- Security flaws
- Authorization bypasses
- Accessibility failures
- Race conditions
- Data-loss risks
- Migration risks
- Incomplete rollback procedures
- Over-mocking
- Tests that pass for the wrong reason
- Unhandled partial failures
- Deployment-specific failures
- Unnecessary complexity
- Scope drift

Do not modify code during the first review pass.

Produce a prioritized report with file references, reproduction steps,
severity, and recommended remediation.


```
Any blocker, critical, or high finding returns the work to implementation.  
  
## 11. Technology-specific requirements  
## React  
Require:  
* Type-safe component interfaces  
* Loading, empty, success, and failure states  
* Keyboard accessibility  
* Responsive behavior  
* Unit tests for complex state  
* Playwright tests for primary flows  
* Screenshot evidence  
* No unreviewed hydration issues  
* No console errors in tested flows  
  
## Node.js  
Require:  
* Input validation  
* Structured error handling  
* Authorization at server boundaries  
* Request logging without sensitive data  
* Graceful shutdown  
* Health checks  
* Unit tests for domain logic  
* Integration tests for APIs and persistence  
* Rate limiting when externally exposed  
  
## PostgreSQL and Prisma  
Require:  
* Explicit constraints  
* Appropriate indexes  
* Transaction boundaries  
* Forward and rollback migration strategy  
* Seed-data impact analysis  
* Generated-client validation  
* Migration testing against a clean database  
* Migration testing against representative existing data  
* Query-plan review for performance-sensitive operations  
Never modify production data directly from an agent without an explicitly approved operational plan.  
  
## Python and machine learning  
Require:  
* Pinned or reproducible environments  
* Deterministic seeds where possible  
* Data-schema validation  
* Dataset-version references  
* Train, validation, and test separation  
* Baseline metrics  
* Evaluation metrics aligned with the use case  
* Model artifact versioning  
* Inference tests  
* Drift or quality monitoring plan  
* Resource requirements  
* CPU, GPU, memory, and latency expectations  
* Clear distinction between experimentation and production code  
For ML changes, the Definition of Done must include measurable acceptance thresholds rather than “the model appears better.”  
Example:  
```

Validation F1 must improve from 0.81 to at least 0.84 without reducing
minority-class recall below 0.78.


```
  
## iOS  
Require:  
* Simulator build  
* Targeted unit tests  
* UI tests for critical flows  
* VoiceOver review  
* Permission-string review  
* Secure Keychain usage for credentials  
* No secrets in the application bundle  
* Network failure handling  
* Offline or interrupted-state behavior where relevant  
* Main-thread safety  
* Memory and lifecycle review  
* Deployment target compatibility  
  
## Docker and cloud  
Require:  
* Multi-stage builds where appropriate  
* Non-root runtime user  
* Minimal runtime image  
* Health check  
* Pinned major dependencies  
* .dockerignore  
* No secrets in image layers  
* Resource limits or recommendations  
* Structured logs  
* Environment-variable documentation  
* Startup and shutdown behavior  
* Container smoke test  
* Rollback or prior-image strategy  
  
## 12. Autonomous execution limits  
Each approved plan must define:  
```

autonomy_budget:
  maximum_iterations: 12
  maximum_cost_usd: 25
  maximum_elapsed_minutes: 120
  maximum_failed_validation_cycles: 3
  stop_on_scope_change: true
  stop_on_destructive_operation: true
  stop_on_unresolved_security_high: true
  stop_on_database_data_loss_risk: true


```
An iteration means one implementation and validation cycle for a workstream.  
The agent must stop when any limit is reached.  
It must produce:  
```

# Budget Stop Report

## Limit Reached

## Work Completed

## Work Remaining

## Current Failures

## Last Known Good Commit

## Rollback Checkpoint

## Recommended Next Action


```
The cost budget should be tracked as an operational ceiling. Where exact model spend is unavailable, the First Mate should record a conservative estimate and clearly label it as estimated.  
  
## 13. Tool and integration layer  
## GitHub  
Use for:  
* Issues  
* Sub-issues or linked issues  
* Branch references  
* Pull requests  
* CI checks  
* Review comments  
* Release tags  
* Rollback tags  
* Security scanning  
Cursor provides a GitHub integration and can also participate in GitHub Actions through its CLI.   
  
## Linear  
Use for:  
* Product backlog  
* Parent tasks  
* Workstream tasks  
* Status tracking  
* Acceptance criteria  
* Linking commits and pull requests  
Suggested statuses:  
```

Backlog
Planning
Awaiting Approval
Approved
In Progress
Validating
Ready for Review
Done
Blocked


```
  
## Notion  
Use for durable product and organizational knowledge:  
* Product requirements  
* Customer research  
* Architecture overviews  
* Meeting decisions  
* Release notes  
* Operational procedures  
Do not make Notion the only location for implementation-critical information. The repository must contain enough context for an agent to work without relying on an external page remaining available.  
  
## MCP servers  
Configure MCP integrations based on project needs:  
* GitHub  
* Notion  
* Linear  
* PostgreSQL read-only development access  
* Cloud platform  
* Documentation retrieval  
* Design tools  
* Browser automation  
* Observability  
* Error tracking  
* Feature flags  
Cursor supports MCP servers for connecting agents to external tools and data.   
Rules for MCP usage:  
1. Use least-privilege credentials.  
2. Prefer read-only access during planning.  
3. Separate development and production credentials.  
4. Never expose MCP secrets in repository files.  
5. Require explicit Captain approval before destructive production operations.  
6. Log external changes in PROGRESS.md.  
7. Link external artifacts in the pull request.  
  
## Playwright and browser automation  
Use for:  
* Browser end-to-end tests  
* Visual evidence  
* Accessibility testing  
* Responsive behavior  
* Form flows  
* Authentication flows  
* Regression reproduction  
Prefer committed Playwright tests over temporary browser-only demonstrations.  
  
## Hooks  
Use hooks to enforce process boundaries such as:  
* Prevent implementation before plan approval  
* Run formatting before commit  
* Run tests before push  
* Prevent secret commits  
* Validate documentation updates  
* Create evidence directories  
* Verify branch naming  
* Verify issue references  
Cursor provides hooks for intercepting and extending agent workflows.   
  
## Cloud agents and headless CLI  
Cloud or headless execution may be used for:  
* CI review  
* Scheduled maintenance  
* Dependency-update verification  
* Test-coverage improvements  
* Repetitive issue triage  
* Documentation checks  
* Large but verifiable migrations  
Cursor supports cloud agents, automations, and non-interactive headless CLI workflows.   
These systems must still obey:  
* Approved scope  
* Iteration limit  
* Cost budget  
* Time limit  
* Validation requirements  
* Stop conditions  
  
## 14. Pull request requirements  
The First Mate creates the pull request only when all required gates pass.  
Template:  
```

## Summary

## Related Issues

Closes #

## Approved Plan

- Plan file:
- Approved revision:
- Approval record:

## Changes

## Architecture

## Database and Migration Impact

## API Impact

## Security Review

## Accessibility Review

## Testing

### Unit

### Integration

### End-to-End

### Build

### Deployment Smoke Test

## Evidence

- Screenshots:
- Test reports:
- Security report:
- Accessibility report:
- Deployment logs:

## Rollback Plan

## Known Limitations

## Deferred Work

## Checklist

- [ ] Plan was approved before implementation
- [ ] Scope matches the approved plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] Security review passes
- [ ] Accessibility review passes
- [ ] Browser evidence is attached
- [ ] Documentation is updated
- [ ] Migration was tested
- [ ] Rollback procedure was tested or reviewed
- [ ] No secrets are included
- [ ] First Mate completed integration review


```
  
## 15. Definition of Done  
A feature is ready only when all applicable conditions are true:  
* The implementation plan was approved.  
* The implementation matches the approved scope.  
* Acceptance criteria are satisfied.  
* Independent workstreams were integrated successfully.  
* Unit tests pass.  
* Integration tests pass.  
* End-to-end tests pass.  
* Relevant browser screenshots exist.  
* Security checks pass.  
* Accessibility checks pass.  
* Production build succeeds.  
* Containers build and start when applicable.  
* Database migrations are validated when applicable.  
* Deployment smoke tests pass when applicable.  
* The rollback method is documented.  
* The adversarial review has no unresolved high-severity findings.  
* Documentation is current.  
* The pull request references the relevant issue.  
* Commits are cohesive and traceable.  
* The First Mate has inspected the final result.  
* PROGRESS.md reflects completion.  
* CHANGELOG.md reflects user-facing changes.  
  
## 16. Master Cursor meta prompt  
  
## 1. Core operating model  
Every project follows the same lifecycle:  
```

Project Intake
    ↓
Repository Discovery
    ↓
Requirements and Risk Analysis
    ↓
Implementation Plan
    ↓
HUMAN APPROVAL GATE
    ↓
Branch and Worktree Provisioning
    ↓
Parallel Implementation
    ↓
Specialist Validation
    ↓
First Mate Integration Review
    ↓
Pull Request and Evidence Package
    ↓
Human Merge or Release Approval
    ↓
Documentation and Memory Update


```
The most important rule is:  
Cursor may investigate, analyze, ask questions, and produce an implementation plan without approval. Cursor must not begin implementation until the implementation plan has been explicitly approved.  
Once approval is given, Cursor may autonomously implement, test, document, commit, open pull requests, and repair failures within the configured iteration, cost, and time limits.  
  
## 2. Agent hierarchy  
## 2.1 The Captain  
The Captain is the human project owner.  
The Captain is responsible for:  
* Defining the product objective  
* Confirming major requirements  
* Reviewing the implementation plan  
* Approving implementation  
* Resolving product decisions that cannot be inferred safely  
* Approving destructive production changes  
* Approving final merge or deployment when required  
The Captain should not need to review every line of code. The system should instead provide evidence that the work satisfies the agreed plan.  
  
## 2.2 The First Mate  
The First Mate is the primary Cursor agent and central coordinator.  
The First Mate must:  
1. Understand the project request.  
2. Inspect the repository.  
3. Identify the project’s technology stack.  
4. Read project memory and decision documents.  
5. Detect missing requirements.  
6. Produce the implementation plan.  
7. Pause for approval.  
8. Convert the approved plan into independent workstreams.  
9. Create branches and worktrees.  
10. Delegate work to specialist agents.  
11. Track agent progress.  
12. Inspect agent results.  
13. resolve code and architectural conflicts.  
14. Rerun failed tasks.  
15. Enforce validation requirements.  
16. Assemble the final integration branch.  
17. Decide whether the feature meets the Definition of Done.  
18. Create or update the pull request.  
19. Produce a completion report.  
20. Update project memory and documentation.  
The First Mate does not simply accept a specialist agent’s claim that a task is finished. It verifies the changed files, tests, logs, screenshots, security findings, accessibility findings, and acceptance criteria itself.  
  
## 2.3 Specialist agents  
Specialists should be created only when their workstreams can be isolated cleanly.  
Recommended roles:  
## Repository Scout  
Inspects the codebase and reports:  
* Architecture  
* Frameworks  
* Runtime versions  
* Package managers  
* Build system  
* Testing infrastructure  
* Deployment infrastructure  
* Database configuration  
* Existing conventions  
* High-risk files  
* Missing documentation  
* Known technical debt  
The Repository Scout does not modify source code.  
## Architecture Agent  
Defines:  
* Components and boundaries  
* API contracts  
* Database changes  
* State-management changes  
* Background processes  
* Deployment effects  
* Security boundaries  
* Migration and rollback strategy  
The Architecture Agent should identify assumptions rather than silently making them.  
## Frontend Agent  
Handles:  
* React components  
* Client-side state  
* Routing  
* Forms  
* Browser behavior  
* Responsive design  
* Accessibility  
* UI tests  
* Screenshot evidence  
## Backend Agent  
Handles:  
* Node.js services  
* REST or GraphQL APIs  
* Business logic  
* Authentication and authorization  
* Background jobs  
* Validation  
* Logging  
* Integration tests  
## Database Agent  
Handles:  
* PostgreSQL schemas  
* Prisma models  
* Migrations  
* Constraints  
* Indexes  
* Transactions  
* Seed data  
* Rollback scripts  
* Query validation  
## Python and ML Agent  
Handles:  
* Python services  
* Data processing  
* Model code  
* Training pipelines  
* Evaluation  
* Inference  
* Reproducibility  
* Dataset contracts  
* Experiment logging  
* Performance benchmarks  
## iOS Agent  
Handles:  
* Swift and SwiftUI  
* UIKit when required  
* Xcode project settings  
* App lifecycle  
* Networking  
* Persistence  
* Permissions  
* Device and simulator testing  
* Accessibility labels  
* iOS-specific security  
## Infrastructure Agent  
Handles:  
* Dockerfiles  
* Docker Compose  
* CI/CD  
* Cloud configuration  
* Secrets interfaces  
* Deployment manifests  
* Health checks  
* Monitoring  
* Rollback procedures  
## Test Engineer  
Creates or verifies:  
* Unit tests  
* Integration tests  
* End-to-end tests  
* Regression tests  
* Failure-path tests  
* Test fixtures  
* Test reports  
## Security Reviewer  
Inspects:  
* Authentication  
* Authorization  
* Input validation  
* Dependency risk  
* Secret exposure  
* Injection risks  
* Unsafe file operations  
* Insecure deserialization  
* Network configuration  
* Cloud permissions  
* Container configuration  
## Accessibility Reviewer  
Inspects:  
* Keyboard navigation  
* Focus order  
* Screen-reader labels  
* Semantic markup  
* Form labeling  
* Error announcements  
* Color contrast  
* Motion sensitivity  
* Touch target sizing  
* iOS VoiceOver behavior  
## Adversarial Reviewer  
Receives the implementation in a fresh context and attempts to prove it incomplete or unsafe.  
It should ask:  
* Which requirement was misunderstood?  
* Which edge case was skipped?  
* What could fail in production?  
* What was tested only through mocks?  
* Which test passes for the wrong reason?  
* What happens during partial failure?  
* Can this change be rolled back?  
* Did implementation drift from the approved plan?  
## Documentation Agent  
Updates:  
* AGENTS.md  
* PROJECT_CONTEXT.md  
* IMPLEMENTATION_PLAN.md  
* DECISIONS.md  
* PROGRESS.md  
* TESTING.md  
* CHANGELOG.md  
* API documentation  
* Setup instructions  
* Deployment instructions  
  
## 3. Standard project structure  
Use this structure in every Cursor-managed repository:  
```

project-root/
├── .cursor/
│   ├── rules/
│   │   ├── 00-core-operating-model.mdc
│   │   ├── 01-planning-and-approval.mdc
│   │   ├── 02-git-and-worktrees.mdc
│   │   ├── 03-testing-and-validation.mdc
│   │   ├── 04-security.mdc
│   │   ├── 05-documentation.mdc
│   │   ├── 06-frontend-react.mdc
│   │   ├── 07-node-backend.mdc
│   │   ├── 08-python-ml.mdc
│   │   ├── 09-ios.mdc
│   │   ├── 10-postgres-prisma.mdc
│   │   └── 11-docker-cloud.mdc
│   │
│   ├── skills/
│   │   ├── repository-discovery/
│   │   │   └── SKILL.md
│   │   ├── implementation-planning/
│   │   │   └── SKILL.md
│   │   ├── worktree-orchestration/
│   │   │   └── SKILL.md
│   │   ├── react-validation/
│   │   │   └── SKILL.md
│   │   ├── node-validation/
│   │   │   └── SKILL.md
│   │   ├── postgres-prisma/
│   │   │   └── SKILL.md
│   │   ├── python-ml-validation/
│   │   │   └── SKILL.md
│   │   ├── ios-validation/
│   │   │   └── SKILL.md
│   │   ├── docker-cloud-validation/
│   │   │   └── SKILL.md
│   │   ├── security-review/
│   │   │   └── SKILL.md
│   │   ├── accessibility-review/
│   │   │   └── SKILL.md
│   │   ├── playwright-evidence/
│   │   │   └── SKILL.md
│   │   └── pull-request-preparation/
│   │       └── SKILL.md
│   │
│   ├── commands/
│   │   ├── initialize-project.md
│   │   ├── plan-feature.md
│   │   ├── implement-approved-plan.md
│   │   ├── validate-change.md
│   │   ├── prepare-pr.md
│   │   └── close-workstream.md
│   │
│   └── hooks/
│       └── README.md
│
├── .agent/
│   ├── runs/
│   ├── evidence/
│   │   ├── screenshots/
│   │   ├── test-results/
│   │   ├── security/
│   │   ├── accessibility/
│   │   └── deployment/
│   ├── handoffs/
│   └── budgets/
│
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── runbooks/
│   └── plans/
│
├── AGENTS.md
├── PROJECT_CONTEXT.md
├── IMPLEMENTATION_PLAN.md
├── DECISIONS.md
├── PROGRESS.md
├── TESTING.md
├── CHANGELOG.md
├── .cursorignore
├── .cursorindexingignore
└── README.md


```
Use the correctly spelled IMPLEMENTATION_PLAN.md. If a project already contains IMPLEMETATION_PLAN.md, Cursor should rename it and update references in the same commit.  
Cursor officially supports project instructions through .cursor/rules/ and AGENTS.md, while Agent Skills allow detailed task-specific guidance to remain unloaded until relevant.   
  
## 4. Documentation responsibilities  
```
AGENTS.md

```
This is the concise operational entry point for every agent.  
It should contain:  
```

# Agent Operating Instructions

## Authority Model

The human user is the Captain.
The primary coordinating agent is the First Mate.

Do not begin implementation until the user explicitly approves the current
IMPLEMENTATION_PLAN.md.

## Required Startup Sequence

1. Read PROJECT_CONTEXT.md.
2. Read DECISIONS.md.
3. Read PROGRESS.md.
4. Read TESTING.md.
5. Inspect the repository status.
6. Identify the active issue and branch.
7. Determine whether an approved plan exists.
8. Load only the Skills relevant to the current task.

## Implementation Rules

- Do not change unrelated files.
- Do not silently expand scope.
- Do not weaken tests to make them pass.
- Do not expose secrets.
- Do not commit generated secrets or environment files.
- Preserve backward compatibility unless the plan approves a breaking change.
- Record architectural decisions in DECISIONS.md.
- Add tests for all behavior changes.
- Maintain rollback capability.
- Use feature branches and isolated worktrees.
- Reference the relevant issue in commits and pull requests.

## Completion Requirements

A task is not complete until:

- Acceptance criteria are satisfied.
- Unit tests pass.
- Integration tests pass.
- End-to-end tests pass when applicable.
- Security checks pass.
- Accessibility checks pass when applicable.
- Browser evidence is captured for UI changes.
- Documentation is updated.
- Rollback instructions exist.
- The First Mate has inspected the final result.


```
  
```
PROJECT_CONTEXT.md

```
This is the repository’s durable context.  
Recommended structure:  
```

# Project Context

## Product Summary

## Intended Users

## Primary User Problems

## Success Metrics

## Current Technology Stack

## Repository Map

## Major Components

## External Services

## Data Sources

## Environments

## Deployment Targets

## Security Boundaries

## Accessibility Expectations

## Performance Expectations

## Known Constraints

## Known Technical Debt

## Terminology

## Important Commands

## Local Development Setup

## Current Priorities


```
This file should describe stable project knowledge. Temporary implementation details belong elsewhere.  
  
```
IMPLEMENTATION_PLAN.md

```
This is the approval-controlled execution contract.  
```

# Implementation Plan

## Status

DRAFT | AWAITING APPROVAL | APPROVED | IN PROGRESS | VALIDATING | COMPLETE

## Request

## Problem Statement

## Desired Outcome

## Non-Goals

## Assumptions

## Open Questions

## Current-State Analysis

## Proposed Architecture

## User Experience Changes

## API Changes

## Database Changes

## Security Impact

## Accessibility Impact

## Infrastructure and Deployment Impact

## Workstreams

### Workstream 1

- Objective:
- Owner agent:
- Files:
- Dependencies:
- Acceptance criteria:
- Tests:
- Branch:
- Worktree:

## Parallelization Plan

## Migration Plan

## Rollback Plan

## Testing Strategy

## Evidence Requirements

## Risks and Mitigations

## Cost, Time, and Iteration Budget

## Definition of Done

## Approval Record

- Approved by:
- Approval message:
- Approval date:
- Approved revision:


```
Any material deviation from the approved plan requires the plan to be amended and returned to the Captain for approval.  
Material deviation includes:  
* New database tables  
* Breaking API changes  
* New paid services  
* Authentication changes  
* Major dependency replacements  
* Destructive migrations  
* Significant scope expansion  
* Major architectural changes  
* Production infrastructure changes not listed in the plan  
  
```
DECISIONS.md

```
Use a lightweight architecture decision record format:  
```

# Decisions

## DEC-001: Decision title

- Date:
- Status: Proposed | Accepted | Superseded | Rejected
- Context:
- Options considered:
- Decision:
- Rationale:
- Consequences:
- Rollback or replacement path:
- Related issue:
- Related pull request:


```
Do not rewrite historical decisions. Add a new decision that supersedes the old one.  
  
```
PROGRESS.md

# Progress

## Current Objective

## Current Phase

## Active Workstreams

| Workstream | Agent | Branch | Status | Last Validation | Blocker |
|---|---|---|---|---|---|

## Completed Work

## Current Failures

## Deferred Work

## Next Action

## Budget Status

- Iterations used:
- Iterations remaining:
- Estimated cost used:
- Cost remaining:
- Elapsed time:
- Time remaining:


```
  
```
TESTING.md

# Testing Strategy

## Test Commands

### Unit

### Integration

### End-to-End

### Security

### Accessibility

### iOS

### Python and ML

### Docker

## Environment Requirements

## Test Fixtures

## Mocking Policy

## Coverage Expectations

## Browser Matrix

## Device Matrix

## Evidence Storage

## Known Test Limitations

## Flaky Test Policy

## Release Validation Checklist


```
  
```
CHANGELOG.md

```
Use a standard structure:  
```

# Changelog

## Unreleased

### Added

### Changed

### Fixed

### Security

### Deprecated

### Removed

## Released Versions


```
  
## 5. Cursor rules  
## Rule 00: Core operating model  
```

---
description: Core operating model for every project
alwaysApply: true
---

You are operating inside the Captain's Compass Engineering System.

The human user is the Captain.
The coordinating agent is the First Mate.

Before performing any work:

1. Read AGENTS.md.
2. Read PROJECT_CONTEXT.md.
3. Read DECISIONS.md.
4. Read PROGRESS.md.
5. Read TESTING.md.
6. Inspect git status and the active branch.
7. Identify whether the task has an approved implementation plan.

Never implement an unapproved plan.

You may perform read-only discovery and planning before approval.
You must pause after producing the implementation plan.

After approval, work autonomously within the approved scope and configured
iteration, cost, and time budgets.

Prefer verifiable outcomes over claims.
Never declare success without evidence.


```
  
## Rule 01: Planning and approval  
```

---
description: Approval-gated planning and implementation
alwaysApply: true
---

For any task that changes application behavior:

1. Investigate the current implementation.
2. Identify assumptions and constraints.
3. Write or update IMPLEMENTATION_PLAN.md.
4. Set its status to AWAITING APPROVAL.
5. Present a concise plan summary to the Captain.
6. Stop before modifying implementation files.

Approval must be explicit.

Acceptable approval examples:

- Approved
- Proceed with the plan
- Begin implementation
- Implement this plan
- Approved with the following changes: ...

After approval:

1. Record the approval in IMPLEMENTATION_PLAN.md.
2. Set the status to APPROVED.
3. Create the issue, branch, worktree, and rollback checkpoint.
4. Begin implementation.


```
  
## Rule 02: Git and worktrees  
```

---
description: Git branch, worktree, commit, and pull request requirements
alwaysApply: true
---

Never implement directly on main, master, develop, or a protected release branch.

For each approved feature:

1. Confirm the repository is clean.
2. Fetch the latest remote state.
3. Create a rollback tag or checkpoint branch.
4. Create an integration feature branch.
5. Create isolated worktrees for independent workstreams.
6. Keep each worktree scoped to one defined responsibility.
7. Commit cohesive changes with issue references.
8. Rebase or merge from the approved base before integration.
9. Run validation after conflict resolution.
10. Open a pull request only after required checks pass.

Branch naming:

feature/<issue>-<short-description>
fix/<issue>-<short-description>
refactor/<issue>-<short-description>
test/<issue>-<short-description>
infra/<issue>-<short-description>

Workstream branch naming:

agent/<issue>-<role>-<short-description>

Commit format:

<type>(<scope>): <summary> (<issue-reference>)

Examples:

feat(auth): add passkey registration flow (#142)
test(api): cover token refresh failures (#142)
docs(deploy): document rollback procedure (#142)


```
Cursor supports isolated local agent work through worktrees, including /worktree and /best-of-n workflows.   
  
## Rule 03: Testing and validation  
```

---
description: Validation requirements for implementation work
alwaysApply: true
---

Every behavior change must have an appropriate automated test.

Required validation layers:

1. Static analysis and type checking.
2. Unit tests.
3. Integration tests.
4. End-to-end tests for user-facing flows.
5. Browser screenshots for visual changes.
6. Security review.
7. Accessibility review.
8. Build validation.
9. Deployment or container smoke test when applicable.
10. Rollback verification when applicable.

Do not:

- Delete a failing test without justification.
- Change an assertion only to match broken behavior.
- over-mock the behavior under test.
- claim browser validation without running it.
- claim security validation based only on linting.
- claim accessibility based only on visual inspection.

Save evidence under .agent/evidence/.


```
  
## Rule 04: Security  
```

---
description: Security requirements
alwaysApply: true
---

Treat all external input as untrusted.

Never:

- Print or commit secrets.
- Add credentials to source files.
- weaken authentication or authorization for convenience.
- bypass certificate validation.
- use unsafe shell interpolation.
- expose detailed internal errors to end users.
- create unrestricted cloud permissions.
- trust client-side authorization.

Review changed code for:

- Injection
- Broken access control
- Authentication failures
- Sensitive data exposure
- Cross-site scripting
- Cross-site request forgery
- Server-side request forgery
- Path traversal
- Unsafe file upload
- Insecure deserialization
- Dependency vulnerabilities
- Container privilege escalation
- Misconfigured CORS
- Insecure mobile storage


```
  
## 6. Workflow phases  
## Phase 0: Project initialization  
The First Mate should perform the following when entering a new repository:  
1. Confirm the repository root.  
2. Run a read-only repository inventory.  
3. Detect languages and frameworks.  
4. Detect package managers.  
5. Detect test frameworks.  
6. Detect Docker and cloud files.  
7. Detect database tooling.  
8. Detect iOS workspaces or Xcode projects.  
9. Detect Python environments and ML artifacts.  
10. Detect CI/CD configuration.  
11. Inspect GitHub issue and pull request conventions.  
12. Inspect existing Cursor rules.  
13. Create missing documentation files.  
14. Create .cursor/rules/ and .cursor/skills/.  
15. Configure .cursorignore.  
16. Document project-specific commands.  
17. Make an initialization commit.  
18. Open a repository setup pull request if the project already uses protected branches.  
The initialization phase should not alter product behavior.  
  
## Phase 1: Request intake  
The First Mate converts the user request into:  
* Problem statement  
* Expected users  
* Desired outcome  
* Acceptance criteria  
* Non-goals  
* Constraints  
* Dependencies  
* Risk level  
* Affected systems  
* Required evidence  
If information is missing, the First Mate should inspect the repository before asking questions. Questions should only cover decisions that materially affect product behavior or architecture.  
  
## Phase 2: Repository discovery  
The Repository Scout should inspect:  
```

git status
git branch --show-current
git log --oneline -n 20
git remote -v
find . -maxdepth 2 -type f


```
It should then inspect relevant manifests, such as:  
```

package.json
pnpm-lock.yaml
yarn.lock
package-lock.json
pyproject.toml
requirements.txt
Pipfile
Podfile
Package.swift
*.xcodeproj
*.xcworkspace
prisma/schema.prisma
Dockerfile
docker-compose.yml
.github/workflows/
terraform/
vercel.json
railway.json
fly.toml


```
The Scout must report findings without changing code.  
  
## Phase 3: Implementation planning  
The First Mate creates IMPLEMENTATION_PLAN.md.  
The plan must include:  
* Exact expected behavior  
* Files or modules likely to change  
* Proposed architecture  
* Workstream boundaries  
* Agent assignments  
* Dependencies between workstreams  
* Git strategy  
* Test strategy  
* Security strategy  
* Accessibility strategy  
* Deployment effect  
* Migration effect  
* Rollback method  
* Cost limit  
* Time limit  
* Iteration limit  
* Definition of Done  
At the end of this phase, Cursor must stop.  
The Captain receives:  
```

Implementation plan ready.

Primary approach:
[summary]

Independent workstreams:
[summary]

Key risks:
[summary]

Validation:
[summary]

Rollback:
[summary]

Status: Awaiting approval.
No implementation has begun.


```
  
## Phase 4: Approval capture  
After approval, the First Mate:  
1. Records the approval wording.  
2. Records the plan revision.  
3. Changes plan status to APPROVED.  
4. Creates or links the project-management issue.  
5. Creates a rollback checkpoint.  
6. Creates the integration branch.  
7. Creates workstream branches.  
8. Creates isolated worktrees.  
9. Updates PROGRESS.md.  
10. Starts specialist agents.  
  
## 7. Git and worktree procedure  
## 7.1 Issue creation  
Create or reference one parent issue for the overall feature.  
Create sub-issues when the project-management platform supports them.  
Example:  
```

Parent issue:
#142 Add organization-based account management

Sub-issues:
#143 Database and Prisma changes
#144 Backend organization API
#145 React organization dashboard
#146 End-to-end and accessibility validation
#147 Deployment and migration verification


```
Each branch, commit, and pull request must reference the relevant issue.  
  
## 7.2 Rollback checkpoint  
Before implementation:  
```

git fetch origin
git checkout main
git pull --ff-only origin main

git tag rollback/<issue>-pre-implementation-<timestamp>
git push origin rollback/<issue>-pre-implementation-<timestamp>


```
If tags are not permitted:  
```

git branch checkpoint/<issue>-pre-implementation
git push origin checkpoint/<issue>-pre-implementation


```
For database work, also capture:  
* Current migration state  
* Schema checksum  
* Backup procedure  
* Down migration or forward-fix procedure  
* Data-preservation assumptions  
  
## 7.3 Integration branch  
```

git checkout -b feature/142-organization-management
git push -u origin feature/142-organization-management


```
  
## 7.4 Worktree creation  
```

mkdir -p ../project-worktrees

git worktree add \
  ../project-worktrees/142-database \
  -b agent/142-database-organization-schema

git worktree add \
  ../project-worktrees/142-backend \
  -b agent/142-backend-organization-api

git worktree add \
  ../project-worktrees/142-frontend \
  -b agent/142-frontend-organization-dashboard

git worktree add \
  ../project-worktrees/142-tests \
  -b agent/142-tests-e2e-accessibility


```
Do not create parallel agents when:  
* Two workstreams must modify the same core files.  
* A later workstream depends on an unsettled API contract.  
* A database schema is still changing.  
* The work is too small to justify coordination overhead.  
* Safe integration boundaries cannot be defined.  
In those cases, execute sequentially.  
  
## 7.5 Worktree contract  
Each specialist receives:  
```

# Workstream Contract

## Parent Issue

## Approved Plan Revision

## Objective

## Allowed Scope

## Expected Files

## Prohibited Files

## Dependencies

## Interface Contract

## Acceptance Criteria

## Required Tests

## Required Evidence

## Branch

## Worktree Path

## Iteration Limit

## Cost Limit

## Time Limit

## Handoff Format


```
A specialist must stop and report rather than silently modify files outside its allowed scope.  
  
## 8. Agent handoff format  
Every specialist returns:  
```

# Agent Handoff

## Workstream

## Status

COMPLETE | PARTIAL | BLOCKED | FAILED

## Summary

## Files Changed

## Design Decisions

## Commands Run

## Test Results

## Security Considerations

## Accessibility Considerations

## Evidence

## Known Limitations

## Remaining Risks

## Commit

## Recommended Integration Order


```
The First Mate verifies each field before integrating.  
  
## 9. Integration process  
The First Mate should integrate in dependency order.  
Typical order:  
1. Shared types and contracts  
2. Database schema  
3. Backend services  
4. Frontend or iOS clients  
5. Infrastructure  
6. End-to-end tests  
7. Documentation  
For each workstream:  
1. Inspect commit history.  
2. Inspect the complete diff.  
3. Confirm scope compliance.  
4. Run workstream tests.  
5. Merge or cherry-pick into the integration branch.  
6. Resolve conflicts.  
7. Run affected tests again.  
8. Update PROGRESS.md.  
9. Record unexpected decisions.  
10. Continue only if the integration remains healthy.  
Conflict resolution must not be delegated blindly to the agent that caused the conflict. The First Mate should reconcile the approved architecture and both workstream contracts.  
  
## 10. Validation pipeline  
## Gate 1: Formatting and static analysis  
Run relevant tools:  
```

ESLint
Prettier
TypeScript compiler
Ruff
Black
mypy
SwiftLint
Swift compiler
Prisma validation
Dockerfile linting
Infrastructure validation


```
Pass condition:  
* No unexplained errors  
* No new critical warnings  
* No disabled rules without justification  
  
## Gate 2: Unit tests  
Required for:  
* Business logic  
* Utility functions  
* React hooks  
* State transitions  
* API handlers  
* Validation  
* Database helpers  
* ML preprocessing  
* Model-evaluation logic  
* Swift view models and services  
The First Mate must review whether tests exercise behavior, not just code paths.  
  
## Gate 3: Integration tests  
Required for interactions such as:  
* API and database  
* Service and external provider  
* Prisma and PostgreSQL  
* Authentication and authorization  
* Python inference service and Node API  
* iOS networking and local persistence  
* Dockerized service communication  
Use real dependencies in containers when practical.  
  
## Gate 4: End-to-end tests  
Use Playwright for browser-based flows.  
Required checks:  
* Happy path  
* At least one validation failure  
* At least one authorization failure  
* Loading state  
* Empty state  
* Error state  
* Refresh or navigation persistence  
* Mobile viewport when relevant  
* Keyboard-only navigation  
Cursor’s browser tooling can control a browser, inspect the UI, test behavior, and audit accessibility.   
Store:  
```

.agent/evidence/test-results/
.agent/evidence/screenshots/


```
Screenshots should include:  
* Initial state  
* Completed state  
* Relevant error state  
* Mobile state  
* Accessibility-sensitive state where useful  
  
## Gate 5: Security review  
Run:  
* Dependency audit  
* Static security analysis  
* Secret scan  
* Changed-code review  
* Authorization boundary tests  
* Input-validation tests  
* Container configuration review  
* Cloud permission review  
The Security Reviewer should produce:  
```

.agent/evidence/security/security-review.md


```
Severity levels:  
```

BLOCKER
CRITICAL
HIGH
MEDIUM
LOW
INFORMATIONAL


```
No unresolved blocker, critical, or high finding may pass the gate.  
Cursor’s Bugbot can supplement this process by reviewing pull requests for bugs, security concerns, and code-quality problems, but it should not replace project-specific testing.   
  
## Gate 6: Accessibility review  
For React applications, check:  
* Semantic structure  
* Accessible names  
* Keyboard navigation  
* Focus visibility  
* Focus trapping  
* Form labels  
* Error association  
* Live-region behavior  
* Contrast  
* Responsive zoom  
* Reduced-motion behavior  
* Automated axe findings  
For iOS, check:  
* VoiceOver labels  
* Traits  
* Reading order  
* Dynamic Type  
* Reduce Motion  
* Sufficient touch targets  
* Contrast  
* Non-color status indicators  
Store:  
```

.agent/evidence/accessibility/accessibility-review.md


```
No unresolved serious or critical accessibility issue may pass.  
  
## Gate 7: Build and packaging  
Validate:  
* Production React build  
* Node production startup  
* Python package or service startup  
* Xcode build  
* Prisma generate and migration validation  
* Docker build  
* Docker runtime health check  
  
## Gate 8: Deployment smoke test  
When infrastructure changes:  
1. Deploy to a preview or staging environment.  
2. Confirm health checks.  
3. Confirm database connectivity.  
4. Confirm required environment variables.  
5. Run critical end-to-end tests.  
6. Capture deployment logs.  
7. Confirm rollback operation.  
8. Record the deployed revision.  
Deployment platforms should be selected based on the repository, for example:  
* Vercel  
* Railway  
* Fly.io  
* AWS  
* Google Cloud  
* Azure  
* Render  
* Kubernetes  
* TestFlight for iOS  
  
## Gate 9: Adversarial review  
Run a fresh-context review after implementation.  
Prompt:  
```

Review this change as an adversarial principal engineer.

Assume the implementation contains at least one important defect.

Compare the implementation against the approved plan and acceptance criteria.

Search specifically for:

- Incorrect assumptions
- Missing edge cases
- Security flaws
- Authorization bypasses
- Accessibility failures
- Race conditions
- Data-loss risks
- Migration risks
- Incomplete rollback procedures
- Over-mocking
- Tests that pass for the wrong reason
- Unhandled partial failures
- Deployment-specific failures
- Unnecessary complexity
- Scope drift

Do not modify code during the first review pass.

Produce a prioritized report with file references, reproduction steps,
severity, and recommended remediation.


```
Any blocker, critical, or high finding returns the work to implementation.  
  
## 11. Technology-specific requirements  
## React  
Require:  
* Type-safe component interfaces  
* Loading, empty, success, and failure states  
* Keyboard accessibility  
* Responsive behavior  
* Unit tests for complex state  
* Playwright tests for primary flows  
* Screenshot evidence  
* No unreviewed hydration issues  
* No console errors in tested flows  
  
## Node.js  
Require:  
* Input validation  
* Structured error handling  
* Authorization at server boundaries  
* Request logging without sensitive data  
* Graceful shutdown  
* Health checks  
* Unit tests for domain logic  
* Integration tests for APIs and persistence  
* Rate limiting when externally exposed  
  
## PostgreSQL and Prisma  
Require:  
* Explicit constraints  
* Appropriate indexes  
* Transaction boundaries  
* Forward and rollback migration strategy  
* Seed-data impact analysis  
* Generated-client validation  
* Migration testing against a clean database  
* Migration testing against representative existing data  
* Query-plan review for performance-sensitive operations  
Never modify production data directly from an agent without an explicitly approved operational plan.  
  
## Python and machine learning  
Require:  
* Pinned or reproducible environments  
* Deterministic seeds where possible  
* Data-schema validation  
* Dataset-version references  
* Train, validation, and test separation  
* Baseline metrics  
* Evaluation metrics aligned with the use case  
* Model artifact versioning  
* Inference tests  
* Drift or quality monitoring plan  
* Resource requirements  
* CPU, GPU, memory, and latency expectations  
* Clear distinction between experimentation and production code  
For ML changes, the Definition of Done must include measurable acceptance thresholds rather than “the model appears better.”  
Example:  
```

Validation F1 must improve from 0.81 to at least 0.84 without reducing
minority-class recall below 0.78.


```
  
## iOS  
Require:  
* Simulator build  
* Targeted unit tests  
* UI tests for critical flows  
* VoiceOver review  
* Permission-string review  
* Secure Keychain usage for credentials  
* No secrets in the application bundle  
* Network failure handling  
* Offline or interrupted-state behavior where relevant  
* Main-thread safety  
* Memory and lifecycle review  
* Deployment target compatibility  
  
## Docker and cloud  
Require:  
* Multi-stage builds where appropriate  
* Non-root runtime user  
* Minimal runtime image  
* Health check  
* Pinned major dependencies  
* .dockerignore  
* No secrets in image layers  
* Resource limits or recommendations  
* Structured logs  
* Environment-variable documentation  
* Startup and shutdown behavior  
* Container smoke test  
* Rollback or prior-image strategy  
  
## 12. Autonomous execution limits  
Each approved plan must define:  
```

autonomy_budget:
  maximum_iterations: 12
  maximum_cost_usd: 25
  maximum_elapsed_minutes: 120
  maximum_failed_validation_cycles: 3
  stop_on_scope_change: true
  stop_on_destructive_operation: true
  stop_on_unresolved_security_high: true
  stop_on_database_data_loss_risk: true


```
An iteration means one implementation and validation cycle for a workstream.  
The agent must stop when any limit is reached.  
It must produce:  
```

# Budget Stop Report

## Limit Reached

## Work Completed

## Work Remaining

## Current Failures

## Last Known Good Commit

## Rollback Checkpoint

## Recommended Next Action


```
The cost budget should be tracked as an operational ceiling. Where exact model spend is unavailable, the First Mate should record a conservative estimate and clearly label it as estimated.  
  
## 13. Tool and integration layer  
## GitHub  
Use for:  
* Issues  
* Sub-issues or linked issues  
* Branch references  
* Pull requests  
* CI checks  
* Review comments  
* Release tags  
* Rollback tags  
* Security scanning  
Cursor provides a GitHub integration and can also participate in GitHub Actions through its CLI.   
  
## Linear  
Use for:  
* Product backlog  
* Parent tasks  
* Workstream tasks  
* Status tracking  
* Acceptance criteria  
* Linking commits and pull requests  
Suggested statuses:  
```

Backlog
Planning
Awaiting Approval
Approved
In Progress
Validating
Ready for Review
Done
Blocked


```
  
## Notion  
Use for durable product and organizational knowledge:  
* Product requirements  
* Customer research  
* Architecture overviews  
* Meeting decisions  
* Release notes  
* Operational procedures  
Do not make Notion the only location for implementation-critical information. The repository must contain enough context for an agent to work without relying on an external page remaining available.  
  
## MCP servers  
Configure MCP integrations based on project needs:  
* GitHub  
* Notion  
* Linear  
* PostgreSQL read-only development access  
* Cloud platform  
* Documentation retrieval  
* Design tools  
* Browser automation  
* Observability  
* Error tracking  
* Feature flags  
Cursor supports MCP servers for connecting agents to external tools and data.   
Rules for MCP usage:  
1. Use least-privilege credentials.  
2. Prefer read-only access during planning.  
3. Separate development and production credentials.  
4. Never expose MCP secrets in repository files.  
5. Require explicit Captain approval before destructive production operations.  
6. Log external changes in PROGRESS.md.  
7. Link external artifacts in the pull request.  
  
## Playwright and browser automation  
Use for:  
* Browser end-to-end tests  
* Visual evidence  
* Accessibility testing  
* Responsive behavior  
* Form flows  
* Authentication flows  
* Regression reproduction  
Prefer committed Playwright tests over temporary browser-only demonstrations.  
  
## Hooks  
Use hooks to enforce process boundaries such as:  
* Prevent implementation before plan approval  
* Run formatting before commit  
* Run tests before push  
* Prevent secret commits  
* Validate documentation updates  
* Create evidence directories  
* Verify branch naming  
* Verify issue references  
Cursor provides hooks for intercepting and extending agent workflows.   
  
## Cloud agents and headless CLI  
Cloud or headless execution may be used for:  
* CI review  
* Scheduled maintenance  
* Dependency-update verification  
* Test-coverage improvements  
* Repetitive issue triage  
* Documentation checks  
* Large but verifiable migrations  
Cursor supports cloud agents, automations, and non-interactive headless CLI workflows.   
These systems must still obey:  
* Approved scope  
* Iteration limit  
* Cost budget  
* Time limit  
* Validation requirements  
* Stop conditions  
  
## 14. Pull request requirements  
The First Mate creates the pull request only when all required gates pass.  
Template:  
```

## Summary

## Related Issues

Closes #

## Approved Plan

- Plan file:
- Approved revision:
- Approval record:

## Changes

## Architecture

## Database and Migration Impact

## API Impact

## Security Review

## Accessibility Review

## Testing

### Unit

### Integration

### End-to-End

### Build

### Deployment Smoke Test

## Evidence

- Screenshots:
- Test reports:
- Security report:
- Accessibility report:
- Deployment logs:

## Rollback Plan

## Known Limitations

## Deferred Work

## Checklist

- [ ] Plan was approved before implementation
- [ ] Scope matches the approved plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] Security review passes
- [ ] Accessibility review passes
- [ ] Browser evidence is attached
- [ ] Documentation is updated
- [ ] Migration was tested
- [ ] Rollback procedure was tested or reviewed
- [ ] No secrets are included
- [ ] First Mate completed integration review


```
  
## 15. Definition of Done  
A feature is ready only when all applicable conditions are true:  
* The implementation plan was approved.  
* The implementation matches the approved scope.  
* Acceptance criteria are satisfied.  
* Independent workstreams were integrated successfully.  
* Unit tests pass.  
* Integration tests pass.  
* End-to-end tests pass.  
* Relevant browser screenshots exist.  
* Security checks pass.  
* Accessibility checks pass.  
* Production build succeeds.  
* Containers build and start when applicable.  
* Database migrations are validated when applicable.  
* Deployment smoke tests pass when applicable.  
* The rollback method is documented.  
* The adversarial review has no unresolved high-severity findings.  
* Documentation is current.  
* The pull request references the relevant issue.  
* Commits are cohesive and traceable.  
* The First Mate has inspected the final result.  
* PROGRESS.md reflects completion.  
* CHANGELOG.md reflects user-facing changes.  
  
## 16. Master Cursor meta prompt  
  
  
  
