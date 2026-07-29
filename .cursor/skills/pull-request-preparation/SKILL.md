---
name: pull-request-preparation
description: Assembles PR description, evidence package, and completion report after validation
---

# Pull Request Preparation

## Use this Skill when

Implementation and validation are complete and the change is ready for Captain review.

## Inputs

- Approved IMPLEMENTATION_PLAN.md
- Commits and branch
- Validation evidence
- Updated documentation

## Procedure

1. Confirm Definition of Done items are satisfied or explicitly waived.
2. Summarize the change against acceptance criteria.
3. Link issue, plan, and evidence paths.
4. List test commands and results.
5. Note risks, follow-ups, and rollback steps.
6. Draft the pull request title and body.
7. Load the `github-integration` Skill:
   - If `gh` (or GitHub MCP) is authenticated, create the remote PR.
   - Otherwise, leave a PR-ready description and local issue placeholder.
8. Update PROGRESS.md and CHANGELOG.md as needed.
9. Produce a First Mate completion report.

See also: `review-fix-loop` when review feedback still needs iterative fixes before this Skill runs.

## Output

PR (remote when possible) or PR-ready description, plus completion report for the Captain.

## Prohibited actions

- Do not auto-merge.
- Do not deploy to production without explicit approval.
- Do not omit failed or skipped validation from the report.
- Do not fail the workflow solely because GitHub auth is unavailable.
