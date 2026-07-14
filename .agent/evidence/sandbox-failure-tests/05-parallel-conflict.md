# Failure test 5 — Parallel conflict

## Scenario (design Part 9 Test 4)

Assign two agents changes that would both touch the same central file:
`src/components/ContactForm.tsx` (Agent A: accessibility labels; Agent B: validation UX).

## First Mate behavioral outcome — **Pass** (2026-07-14)

Recognized unsafe parallelization: shared UI component with overlapping responsibility and no stable interface boundary.

**Converted to sequential execution:**

1. Agent A completes accessibility label updates on `ContactForm.tsx` + evidence.
2. Rebase / handoff on the same feature branch.
3. Agent B applies validation UX changes afterward on the updated file.

No parallel worktrees created for this conflicting pair (per worktree-orchestration Skill: do not parallelize shared central files).

## Result

**Pass** — sequentialized; no conflicting parallel worktrees.
