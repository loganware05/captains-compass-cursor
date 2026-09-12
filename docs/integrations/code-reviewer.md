# NorthStar Code Reviewer

Hermetic, evidence-only code review pipeline for NorthStar (M27).

## Pipeline

```
detect → investigate → verify → report
```

1. **Detect** — domains from changed paths + intent from `IMPLEMENTATION_PLAN.md`
2. **Investigate** — context pack (diff, snippets, neighbors); secrets redacted
3. **Verify** — confidence + evidence-path gate (discards noise)
4. **Report** — `.agent/evidence/code-review/<run-id>/{report.json,report.md,context-pack.json}`

## CLI

From the control repo:

```bash
./scripts/run-code-review.sh --repo-root /path/to/repo \
  --plan IMPLEMENTATION_PLAN.md \
  --candidates tests/fixtures/code-review/candidates.json

./scripts/northstar review --repo /path/to/repo --diff-file path/to.diff
```

## Locks (Captain)

- Hermetic CI — fixture/heuristic candidates only; no model calls by default
- Skill slug: `code-reviewer`
- **No GitHub review posting** in M27 (Phase B)
- Tracker: GitHub issues only

## Compose with

- `security-review`, `accessibility-review`, `adversarial-reviewer`
- Downstream: `review-fix-loop` consumes verified findings

## Schema

`orchestrator/schemas/code-review-report.schema.json`
