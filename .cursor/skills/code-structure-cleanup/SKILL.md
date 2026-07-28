---
name: code-structure-cleanup
description: After a feature works, extracts duplicated mechanics into service-layer modules under a separate approved plan without changing behavior
---

# Code Structure Cleanup

## Use this Skill when

A feature already works locally, but the touched code has duplicated runtime mechanics, repeated API calls, repeated parsing/validation, or messy structure that will confuse future agents.

## Inputs

- Files touched by the completed feature
- A **separate** approved `IMPLEMENTATION_PLAN.md` for this cleanup (required)
- Project test commands from `TESTING.md`

## Approval rule (hard)

Cleanup that modifies product implementation files **always** requires its own `IMPLEMENTATION_PLAN.md` at **APPROVED** status.

Do **not** fold cleanup into the original feature plan after the fact. Do **not** start cleanup while the feature plan is still open unless the Captain has approved a distinct cleanup plan.

## Procedure

1. Confirm the feature is green (relevant tests pass or blockers are documented).
2. Confirm a cleanup-specific plan is **APPROVED**.
3. Inspect only the feature area (and direct callers), not the whole app.
4. Name each duplication clearly (e.g. “three slightly different sendEmail helpers”).
5. Propose the smallest service-layer extraction:
   - UI/route/action keeps **domain policy** (what should happen)
   - Service module owns **mechanics** (how it happens: API calls, parsing, streaming, I/O)
6. Implement without changing user-facing behavior.
7. Run applicable validation; capture evidence if required by DoD.
8. Summarize what got simpler and what was deliberately left alone.

## Output

Focused cleanup diff, validation evidence, and a short “what simplified” report for the Captain.

## Prohibited actions

- Redesigning the whole application
- Mixing new features into the cleanup PR
- Changing user-facing behavior “while we’re here”
- Moving domain/business decisions into generic services
- Renaming broadly for aesthetics
- Proceeding without a separate approved cleanup plan
