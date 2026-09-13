# NorthStar Code Reviewer

Hermetic, evidence-only code review pipeline for NorthStar (M27).

## Pipeline

```
detect → investigate → specialist composition → verify → report
```

1. **Detect** — domains from changed paths + intent from `IMPLEMENTATION_PLAN.md`
2. **Investigate** — context pack (diff, snippets, neighbors); secrets redacted
3. **Specialists (M28 default)** — hermetic security / adversarial / testing emitters produce candidate JSON
4. **Verify** — confidence + evidence-path gate (discards noise)
5. **Report** — `.agent/evidence/code-review/<run-id>/{report.json,report.md,context-pack.json}`

## CLI

From the control repo:

```bash
./scripts/run-code-review.sh --repo-root /path/to/repo \
  --plan IMPLEMENTATION_PLAN.md \
  --candidates tests/fixtures/code-review/candidates.json

./scripts/northstar review --repo /path/to/repo --diff-file path/to.diff
./scripts/northstar review --repo /path/to/repo --candidates-mode specialists
./scripts/northstar review --repo /path/to/repo --candidates-mode heuristics  # M27 escape hatch
```

## Locks (Captain)

- Hermetic CI — fixture / specialist / heuristic candidates only; no model calls by default
- Default candidates mode: **specialists** (M28)
- Skill slug: `code-reviewer`
- **No GitHub review posting** in M27 (Phase B)
- Tracker: GitHub issues only

## Compose with

- `security-review`, `accessibility-review`, `adversarial-reviewer`
- Downstream: `review-fix-loop` consumes verified findings

## Schema

`orchestrator/schemas/code-review-report.schema.json`
