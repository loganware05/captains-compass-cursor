---
name: testing-validation
description: Runs applicable validation layers and records evidence for Definition of Done
---

# Testing and Validation

## Use this Skill when

Validating an implemented change, preparing a PR, or verifying Definition of Done.

## Inputs

- Approved plan acceptance criteria
- Changed files
- Project test commands from TESTING.md / package scripts
- Autonomy budget limits

## Procedure

1. Identify applicable validation layers for the change.
2. Run static analysis / lint when available.
3. Run unit and integration tests for affected areas.
4. Run end-to-end or browser checks for UI changes.
5. Capture screenshots and logs under .agent/evidence/.
6. Confirm build succeeds when applicable.
7. Review rollback instructions against the change.
8. For release closeout, run `./scripts/run-sandbox-release-smokes.sh` and gate with
   `./scripts/validate-sandbox-release-smokes.sh --version X.Y.Z` (M18).
9. If tests fail, fix implementation or report a blocker—never weaken tests to pass.
10. Stop and report if budget limits are exceeded.

## Output

Validation report with commands run, results, evidence paths, and remaining gaps.

## Prohibited actions

- Do not delete or weaken failing tests to force a green result.
- Do not claim validation passed without evidence.
- Do not skip applicable security or accessibility checks for UI/API changes.
