---
name: finishing-a-development-branch
description: Use when implementation is complete and tests pass — present Captain integration options and worktree cleanup guidance
---

# Finishing a Development Branch

Patterns inspired by [obra/superpowers](https://github.com/obra/superpowers)
`finishing-a-development-branch` (DISCOVERED inspiration — not a plugin install).

## Use this Skill when

- Implementation and validation are complete (green suite)
- You need Captain choice on how to integrate the branch
- A Git worktree may need cleanup after handoff

## Inputs

- Feature branch name and base branch
- Validation evidence paths
- Whether the checkout is a linked worktree

## Procedure

1. **Verify tests** with Skill `verification-before-completion`. If failing, stop —
   do not present the integration menu.
2. **Detect environment**
   - Normal repo vs linked worktree (`git rev-parse --git-dir` vs `--git-common-dir`)
   - Confirm base branch (from plan / upstream; ask if unclear)
3. **Present Captain options** (do not auto-merge):
   - **Open / update PR** (default under standing order after plan approval)
   - **Keep branch** for more work (no cleanup)
   - **Discard branch** (only with explicit Captain confirmation; never force-push
     protected bases)
4. Execute only the chosen option. Load `pull-request-preparation` /
   `github-integration` for PR path.
5. **Worktree cleanup** only when Captain chose discard or after PR is opened and
   Captain asked to remove the worktree — prefer documented `git worktree remove`
   after branch is pushed/preserved. Never delete uncommitted Captain work.

## Output

Captain-facing menu result, PR URL or next-step note, cleanup status.

## Prohibited actions

- Do not merge to `main` / protected bases without explicit Captain merge action
- Do not force-push protected branches
- Do not discard a dirty worktree without Captain confirmation
- Do not skip fresh verification before claiming ready to finish
