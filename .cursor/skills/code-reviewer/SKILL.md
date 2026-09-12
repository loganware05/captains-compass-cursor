---
name: code-reviewer
description: Runs NorthStar Detection → Investigation → Verification → Review pipeline and writes evidence-only code review reports
---

# Code Reviewer

## Use this Skill when

A branch, PR, or local diff needs a structured NorthStar code review that:

- loads **intent** from `IMPLEMENTATION_PLAN.md` / acceptance criteria
- investigates changed files + related neighbors
- verifies candidate findings before reporting
- writes evidence under `.agent/evidence/code-review/<run-id>/`

## Inputs

- Repository root (control or sandbox)
- Optional git base/head refs, unified diff file, or changed-path list
- Optional fixture candidates JSON (required for hermetic CI / no model)
- Optional plan path (defaults to `IMPLEMENTATION_PLAN.md`)

## Procedure

1. **Detect** — identify domains from changed paths; load plan acceptance criteria / non-goals.
2. **Investigate** — assemble a context pack (diff excerpt, changed file snippets, neighbors). Redact secrets.
3. **Candidates** — use `--candidates` fixtures in CI; otherwise deterministic heuristics only (no model in default path).
4. **Verify** — discard findings below confidence threshold or without evidence paths.
5. **Report** — write `report.json` + `report.md` under `.agent/evidence/code-review/<run-id>/`.
6. Hand verified findings to humans or `review-fix-loop`. **Never auto-merge. Never auto-post GitHub reviews in M27.**

### CLI

```bash
# From control repo
./scripts/run-code-review.sh --repo-root /path/to/repo --plan IMPLEMENTATION_PLAN.md
./scripts/northstar review --repo /path/to/repo --candidates tests/fixtures/code-review/candidates.json
```

## Output

- Schema-valid `report.json` (`code-review-report.schema.json`)
- Human-readable `report.md`
- Optional `context-pack.json`

## Prohibited actions

- Posting GitHub Pull Request Reviews / inline comments (deferred to Phase B)
- Invoking models in CI / default hermetic path
- Auto-merging or auto-fixing without a separate approved plan
- Expanding webhook `pull_request` handling in this Skill
