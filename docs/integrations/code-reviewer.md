# NorthStar Code Reviewer

Hermetic, evidence-only code review pipeline for NorthStar (M27–M29).

## Pipeline

```
detect → investigate → specialist composition → verify → report
```

1. **Detect** — domains from changed paths + intent from plan markdown **or** intent-pack JSON (M29)
2. **Investigate** — context pack (diff, snippets, neighbors); secrets redacted
3. **Specialists (M28 default)** — hermetic security / adversarial / testing emitters produce candidate JSON
4. **Verify** — confidence + evidence-path gate (discards noise)
5. **Report** — `.agent/evidence/code-review/<run-id>/{report.json,report.md,context-pack.json}`

## Intent packs (M29)

Product repos can carry reviewable intent without a hand-written temp plan:

| Artifact | Role |
|---|---|
| `IMPLEMENTATION_PLAN.md` | Primary plan; installer template includes AC / Non-Goals / Rollback / Security / Domains |
| `INTENT_PACK.md` | Optional companion markdown with the same review sections |
| `.agent/intent/current.json` | Normalized JSON (`northstar.intent_pack.v1`); auto-discovered |

Intent packs **never** originate Captain approval (`captain_approval` is always `false`).
Linear export is read-only flight-recorder input:

```bash
./scripts/export-intent-from-linear.sh --out .agent/intent/current.json \
  --fixture tests/fixtures/code-review/linear-issue.json

./scripts/northstar intent export --out .agent/intent/current.json --fixture path/to/issue.json
```

Installer installs `INTENT_PACK.md` when missing and creates `.agent/intent/`.
Existing `IMPLEMENTATION_PLAN.md` (including APPROVED plans) is never overwritten
unless you replace it manually — `--force` refreshes Cursor package files only.

## CLI

From the control repo:

```bash
./scripts/run-code-review.sh --repo-root /path/to/repo \
  --plan IMPLEMENTATION_PLAN.md \
  --candidates tests/fixtures/code-review/candidates.json

# Intent JSON only (no temp plan)
./scripts/run-code-review.sh --repo-root /path/to/repo \
  --intent-json .agent/intent/current.json \
  --diff-file path/to.diff

./scripts/northstar review --repo /path/to/repo --diff-file path/to.diff
./scripts/northstar review --repo /path/to/repo --candidates-mode specialists
./scripts/northstar review --repo /path/to/repo --intent-json .agent/intent/current.json
./scripts/northstar review --repo /path/to/repo --candidates-mode heuristics  # M27 escape hatch
```



## GitHub draft posting (M30)

Default remains **evidence-only**. Opt-in draft posting:

```bash
./scripts/run-code-review.sh --repo-root /path/to/repo \
  --post-github-draft \
  --github-repo loganware05/captain-compass-sandbox \
  --pull-number 123 \
  --diff-file path/to.diff

./scripts/northstar review --repo /path/to/repo \
  --post-github-draft --github-repo owner/name --pull-number 123
```

Gates:

- Explicit `--post-github-draft` (off by default)
- Repo must appear in `.agent/review/github-allowlist.yml`
- Only **verified** findings at/above severity floor (default `medium`)
- Creates a **PENDING** draft review (never APPROVE / REQUEST_CHANGES)
- Token from `GITHUB_TOKEN` / `GH_TOKEN` — never logged
- Evidence written to `.agent/evidence/code-review/<run-id>/github-draft.json`

## Locks (Captain)

- Hermetic CI — fixture / specialist / heuristic candidates only; no model calls by default
- Default candidates mode: **specialists** (M28)
- Skill slug: `code-reviewer`
- **GitHub draft posting opt-in only** (M30); default remains evidence-only
- Intent packs are evidence only; Linear never approves
- Tracker: GitHub issues only

## Compose with

- `security-review`, `accessibility-review`, `adversarial-reviewer`
- Downstream: `review-fix-loop` consumes verified findings

## Schemas

- `orchestrator/schemas/code-review-report.schema.json`
- `orchestrator/schemas/intent-pack.schema.json`
