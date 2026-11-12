---
name: subagent-driven-development
description: Use when executing an APPROVED implementation plan with independent tasks — dispatch a fresh implementer per task, review after each, keep going with recorded Rulings
---

# Subagent-Driven Development

Patterns inspired by [obra/superpowers](https://github.com/obra/superpowers)
`subagent-driven-development` (DISCOVERED inspiration — not a plugin install).

**Playbook only.** Does not expand Captain authority or bypass NorthStar stop rules.

## Use this Skill when

- `IMPLEMENTATION_PLAN.md` is **APPROVED**
- Tasks are mostly independent
- Subagent / worktree tools are available and the Captain did not require inline-only

Prefer Skill `worktree-orchestration` when file boundaries need isolation.

## Core principle

Fresh implementer context per task + task review (spec + quality) + final
branch review. The coordinator preserves context; children do not inherit the
full chat history — give them exactly what they need.

## Procedure

1. Confirm plan **APPROVED** and rollback/branch exist.
2. For each plan task (in dependency order):
   - Dispatch a fresh implementer with task brief, file boundaries, acceptance
     checks, and pointers to Skills — not the entire session.
   - After the task, run a focused review (spec compliance + obvious defects).
   - Fix small findings yourself; re-dispatch only for material gaps.
3. **Continuous execution:** do not pause for “should I continue?” between tasks
   once the Captain approved the plan. Record mid-flight decisions as:
   `Ruling: <what> — <why> — <cost if wrong>` and proceed.
4. **Stop and ask** only for:
   - irreversible / destructive operations
   - security-sensitive actions
   - side effects outside this worktree that norms require asking (merge, push
     to shared branch, publish)
   - a plan so broken every path forward is a guess
5. When all tasks complete, load `verification-before-completion`, then
   `finishing-a-development-branch` / `pull-request-preparation`.

## Output

Task ledger with reviews/Rulings, validation evidence, PR-ready branch.

## Prohibited actions

- Do not start without an APPROVED plan
- Do not override NorthStar approval, security, or protected-branch rules
- Do not auto-merge or deploy
- Do not install third-party Superpowers plugins
- Do not silently expand scope past the plan (return to approval gate instead)
