---
name: implementation-planning
description: Creates an approval-gated implementation plan before product changes
---

# Implementation Planning

## Use this Skill when

Use this Skill for any feature, bug fix, refactor, database change,
infrastructure change, or other task that modifies product behavior.

## Inputs

- User request
- Repository structure
- Existing project documentation
- Current Git state
- Relevant issue
- Technical constraints

## Procedure

1. Read the required project documents.
2. Inspect relevant implementation files.
3. Load Skill `capability-planning` and run `./scripts/capability-plan.sh` for the objective; merge rendered sections into `IMPLEMENTATION_PLAN.md`.
4. Identify current behavior.
5. Define desired behavior.
6. Identify assumptions and open questions.
7. Identify affected systems.
8. Define independent workstreams (align with task graph when present).
9. Define tests and evidence.
10. Define migration and rollback requirements.
11. Define time, cost, and iteration limits.
12. Write IMPLEMENTATION_PLAN.md.
13. Set its status to AWAITING APPROVAL.
14. Present the plan and stop.

## Output

A complete IMPLEMENTATION_PLAN.md ready for human approval.

## Prohibited actions

- Do not modify product implementation files.
- Do not create migrations.
- Do not begin a feature branch.
- Do not claim that approval is implied.
