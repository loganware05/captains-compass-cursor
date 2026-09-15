---
name: code-reviewer
description: Runs NorthStar Detection → Investigation → Verification → Review pipeline and writes evidence-only code review reports
---

# Code Reviewer

## Use this Skill when

A branch, PR, or local diff needs a structured NorthStar code review that:

- loads **intent** from `IMPLEMENTATION_PLAN.md`, `INTENT_PACK.md`, or `--intent-json`
  (normalized `northstar.intent_pack.v1`; never sets Captain approval)
- investigates changed files + related neighbors
- verifies candidate findings before reporting
- writes evidence under `.agent/evidence/code-review/<run-id>/`

## Inputs

- Repository root (control or sandbox)
- Optional git base/head refs, unified diff file, or changed-path list
- Optional fixture candidates JSON (required for hermetic CI / no model)
- Optional plan path (defaults to `IMPLEMENTATION_PLAN.md` / `INTENT_PACK.md` auto-discover)
- Optional `--intent-json` normalized intent pack (M29)

## Procedure

1. **Detect** — identify domains from changed paths; load plan or intent-pack acceptance criteria / non-goals.
2. **Investigate** — assemble a context pack (diff excerpt, changed file snippets, neighbors). Redact secrets.
3. **Candidates** — default **specialists** mode composes hermetic security / adversarial / testing emitters (M28). Use `--candidates` fixtures in CI; `--candidates-mode heuristics` is the M27 escape hatch. No model in the default path.
4. **Verify** — discard findings below confidence threshold or without evidence paths.
5. **Report** — write `report.json` + `report.md` under `.agent/evidence/code-review/<run-id>/`.
6. Hand verified findings to humans or `review-fix-loop`. **Never auto-merge.** GitHub draft posting is **opt-in** (`--post-github-draft`) and allowlist-gated (M30); default remains evidence-only.
7. **Outcomes (M31)** — after human triage, record outcomes → Experience (optional RoutingProposal is proposal-only).
8. **Repair (M32/B4)** — optional supervised dry-run from a verified finding (`northstar repair start`); never auto-merges.

### CLI

```bash
# From control repo
./scripts/run-code-review.sh --repo-root /path/to/repo --plan IMPLEMENTATION_PLAN.md
./scripts/run-code-review.sh --repo-root /path/to/repo --intent-json .agent/intent/current.json
./scripts/northstar review --repo /path/to/repo --candidates-mode specialists
./scripts/northstar review --repo /path/to/repo --candidates tests/fixtures/code-review/candidates.json
./scripts/northstar intent export --out .agent/intent/current.json --fixture issue.json
./scripts/northstar outcomes record --report path/to/report.json --triage path/to/triage.json
./scripts/record-finding-outcomes.sh --report path/to/report.json --triage path/to/triage.json --emit-routing-proposal
./scripts/northstar repair start --report path/to/report.json --finding-id FINDING_ID
./scripts/run-repair.sh --report path/to/report.json --finding-id FINDING_ID \
  --target-repository loganware05/captain-compass-sandbox
```

## Output

- Schema-valid `report.json` (`code-review-report.schema.json`)
- Human-readable `report.md`
- Optional `context-pack.json`
- Optional triage `outcomes.json` + Experience lessons; optional RoutingProposal (`auto_apply=false`)
- Optional repair evidence under `.agent/evidence/repair/<run-id>/` (dry-run; never auto-merge)

## Prohibited actions

- Auto-applying RoutingProposal / Skill confidence deltas (Captain gate only)
- Auto-merging repair PRs (B4 SUBMIT is draft/human-reviewed only)
- Invoking models in CI / default hermetic path
- Auto-merging or auto-fixing without a separate approved plan
- Expanding webhook `pull_request` handling in this Skill
- Treating Linear as Captain approval authority
