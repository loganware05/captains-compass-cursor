---
name: worktree-orchestration
description: Creates branches, rollback checkpoints, and isolated Git worktrees for approved work
---

# Worktree Orchestration

## Use this Skill when

An implementation plan has been approved and work must be provisioned safely,
or when parallel workstreams need isolated checkouts.

## Inputs

- Approved IMPLEMENTATION_PLAN.md
- Issue reference
- Base branch
- Workstream file boundaries

## Procedure

1. Confirm plan status is APPROVED with an approval record.
2. Confirm current branch is not a protected base branch.
3. Create or reference the issue.
4. Record a rollback checkpoint (annotated tag or documented SHA).
5. Create the feature/fix branch with the required naming convention.
6. Create isolated worktrees only when workstreams are cleanly separable.
7. If workstreams share central files, convert to sequential execution.
8. Hand off paths and branch names to specialist agents.

## Output

Branch names, worktree paths, rollback checkpoint reference, and workstream assignment map.

## Prohibited actions

- Do not implement on main, master, develop, or protected release branches.
- Do not create parallel worktrees that will conflict on the same files.
- Do not proceed without an approved plan.
