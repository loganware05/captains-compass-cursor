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
3. Identify current behavior.
4. Define desired behavior.
5. Identify assumptions and open questions.
6. Identify affected systems.
7. Define independent workstreams.
8. Define tests and evidence.
9. Define migration and rollback requirements.
10. Define time, cost, and iteration limits.
11. Write IMPLEMENTATION_PLAN.md.
12. Set its status to AWAITING APPROVAL.
13. Present the plan and stop.

## Output

A complete IMPLEMENTATION_PLAN.md ready for human approval.

## Prohibited actions

- Do not modify product implementation files.
- Do not create migrations.
- Do not begin a feature branch.
- Do not claim that approval is implied.
