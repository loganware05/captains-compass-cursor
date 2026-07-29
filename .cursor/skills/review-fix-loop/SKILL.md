---
name: review-fix-loop
description: Iterates on PR or review feedback for a small change until tests pass and the review is clean or a human decision is required
---

# Review-Fix Loop

## Use this Skill when

A small PR or feature branch has actionable review feedback (human, Bugbot, Greptile-style tools, adversarial-reviewer report, or CI review comments) and the success condition is clear.

## Inputs

- Current branch / PR
- Review feedback (paste, `gh` review comments, or evidence path)
- Required end state (e.g. tests pass, review threads resolved, no unrelated rewrites)
- Project test commands from `TESTING.md`

## Procedure

1. **Preflight:** If the PR is too large for a reliable loop, stop and propose a split. Do not start the loop on huge diffs.
2. Read the full PR diff (or `git diff` against the base branch).
3. Read the review feedback carefully.
4. Classify each item: real/relevant, false positive, or needs human product decision.
5. Fix only real/relevant items. Add or update tests when fixing a bug.
6. Run applicable validation (`testing-validation` Skill).
7. Summarize resolved items and remaining open questions.
8. If more feedback arrives, repeat from step 2.
9. Stop when the PR is clean **or** blocked on a Captain decision. Hand off to `pull-request-preparation` when ready.

## Output

Updated branch with fixes, validation evidence, and a loop summary (resolved vs deferred vs needs human).

## Prohibited actions

- Auto-merging
- Blindly accepting every review comment
- Unrelated refactors or scope expansion
- Continuing past autonomy budget without a Budget Stop Report
- Treating a clean review as proof the product is valuable—only that this diff looks sound
