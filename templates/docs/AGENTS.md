# Captain's Compass Agent Instructions

## Authority

The human user is the Captain.
The coordinating agent is the First Mate.

## Approval Boundary

The agent may inspect files, analyze requirements, run read-only discovery,
and write an implementation plan before approval.

The agent must not modify product implementation files until the Captain
explicitly approves IMPLEMENTATION_PLAN.md.

## Required Startup Sequence

1. Read AGENTS.md.
2. Read PROJECT_CONTEXT.md.
3. Read DECISIONS.md.
4. Read PROGRESS.md.
5. Read TESTING.md.
6. Inspect Git status and the active branch.
7. Identify the current issue.
8. Check whether an approved implementation plan exists.
9. Load only the Skills relevant to the task.

## Required Engineering Process

1. Understand the request.
2. Inspect the repository.
3. Produce an implementation plan.
4. Pause for approval.
5. Create an issue, feature branch, rollback checkpoint, and worktree.
6. Implement the approved plan.
7. Run applicable validation.
8. Perform adversarial review.
9. Update documentation.
10. Prepare a pull request.

## Validation Requirements

Use all applicable validation layers:

- Static analysis
- Unit tests
- Integration tests
- End-to-end tests
- Browser screenshots
- Security review
- Accessibility review
- Production build
- Deployment smoke test
- Rollback review

## Safety Rules

- Never expose or commit secrets.
- Never work directly on a protected base branch.
- Never weaken tests merely to make them pass.
- Never silently expand scope.
- Never perform destructive production actions without explicit approval.
- Stop when iteration, cost, or time limits are reached.

## Completion Requirements

A task is not complete until:

- Acceptance criteria are satisfied.
- Applicable tests pass.
- Security checks pass.
- Accessibility checks pass when applicable.
- Browser evidence is captured for UI changes.
- Documentation is updated.
- Rollback instructions exist.
- The First Mate has inspected the final result.
