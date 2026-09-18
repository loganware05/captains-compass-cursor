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
8. **Repair (M32 / B4)** — for verified findings only, `northstar repair start` builds a FIND→PROVE→dispatch packet. Never auto-merges. Captain authorization required before FIX/SUBMIT.
9. **Precision (M33 / B5)** — aggregate finding outcomes into a precision ledger + dashboard; optional priority proposal never auto-applies.

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
./scripts/northstar repair start --report path/to/report.json --finding <id> --repository loganware05/captain-compass-sandbox
./scripts/start-repair-loop.sh --report path/to/report.json --finding <id> --repository loganware05/captain-compass-sandbox
./scripts/northstar precision aggregate --outcomes path/to/outcomes.json --emit-priority-proposal
./scripts/aggregate-precision-ledger.sh --outcomes path/to/outcomes.json --ledger-id demo
```

## M40: cross-boundary verification gate

When the repo has a built inode store (Skill `context-inodes`), the pipeline
emits deterministic **boundary candidates** for calls/imports that cross
context routes (`domain/module`):

- `boundary-unknown-symbol` (high) — import names a symbol the callee inode
  does not export
- `boundary-arity` (medium) — added call site passes an argument count the
  declared signature cannot accept
- `boundary-complexity` (medium) — added call inside an added loop invokes a
  callee with non-constant declared `@complexity` (e.g. declared \(O(N)\)
  called per element ⇒ effective \(O(N^2)\))

The gate is on by default (`--boundary-check`); it **skips with an explicit
note** when the inode store is absent or stale — never review against
untrusted metadata. Boundary findings carry `category: boundary` and flow
through the standard verify/rank path. Precision target on fixture + sandbox
corpora: 1.0 (measured in `tests/evals/run.sh` M40 sensors).

## Output

- Schema-valid `report.json` (`code-review-report.schema.json`)
- Human-readable `report.md`
- Optional `context-pack.json`
- Optional triage `outcomes.json` + Experience lessons; optional RoutingProposal (`auto_apply=false`)
- Optional repair `repair-run.json` + `dispatch-packet.json` under `.agent/evidence/repair/<run-id>/`
- Report provenance records `boundary` notes/candidate counts

## Prohibited actions

- Auto-applying RoutingProposal / Skill confidence deltas (Captain gate only)
- Invoking models in CI / default hermetic path
- Auto-merging or auto-fixing without a separate approved plan
- Repairing unverified or discarded findings
- Expanding webhook `pull_request` handling in this Skill
- Treating Linear as Captain approval authority
