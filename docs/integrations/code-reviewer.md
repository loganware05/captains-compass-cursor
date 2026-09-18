# NorthStar Code Reviewer

Hermetic, evidence-only code review pipeline for NorthStar (M27–M31).

## Pipeline

```
detect → investigate → specialist composition → boundary gate (M40) → verify → report
```

1. **Detect** — domains from changed paths + intent from plan markdown **or** intent-pack JSON (M29)
2. **Investigate** — context pack (diff, snippets, neighbors); secrets redacted
3. **Specialists (M28 default)** — hermetic security / adversarial / testing emitters produce candidate JSON
4. **Boundary gate (M40)** — cross-boundary checks against metadata inodes (below)
5. **Verify** — confidence + evidence-path gate (discards noise)
6. **Report** — `.agent/evidence/code-review/<run-id>/{report.json,report.md,context-pack.json}`

## Cross-boundary verification gate (M40)

When the repo has a built inode store (`scripts/build-context-inodes.sh`; see
[`context-inodes.md`](context-inodes.md)), the gate validates imports/calls
that cross context routes (`domain/module`) against callee metadata:

| Check | Severity | Fires when |
|---|---|---|
| `boundary-unknown-symbol` | high | an import names a symbol the callee does not export (both directions: changed importers and unchanged importers of a changed callee) |
| `boundary-arity` | medium | an added call passes an argument count the declared signature cannot accept (variadic-aware) |
| `boundary-complexity` | medium | an added call inside an added loop invokes a callee with non-constant declared `@complexity` (e.g. \(O(N)\) per element ⇒ \(O(N^2)\)) |

- On by default; `--no-boundary-check` disables. Absent/stale store ⇒ the gate
  **skips with an explicit note** (never reviews against untrusted metadata).
- New files are checked via their added import lines even when unindexed.
- Effective callee exports = store exports − diff-removed + diff-added, so
  verdicts are correct whether the store was built from base or head.
- Deterministic and hermetic; findings carry `category: boundary` and flow
  through the standard verify/rank path. Precision 1.0 on the fixture and
  sandbox corpora (measured; see `.agent/evidence/m40-filesystem-gated-context/`).
- Known limits: TS parser-lite subset (no `export *` expansion); complexity is
  declared-metadata conformance, not static inference.

## Agentic-equivalent fail-closed checks (M37)

Cursor Agentic Security Review reasons about *control effectiveness* (not only
secret regexes). NorthStar encodes the PR #7 medium classes as hermetic
`security-review` specialist candidates when the diff touches `.cursor/hooks/**`
or `hooks.json`:

| Finding id | Class |
|---|---|
| `sec-hook-plan-self-serve` | Plan-approval self-serve via exempt `IMPLEMENTATION_PLAN.md` Write |
| `sec-hook-checkout-shortcircuit` | Protected-branch `checkout -b feature/` substring allow |
| `sec-hook-push-refspec-gap` | Push without refspec / `HEAD:main` awareness |
| `sec-hook-git-c-gap` | Missing `git -C` target-repo resolution |

Fixtures: `tests/fixtures/code-review/hook-*.diff` and
`intent-security-hooks.json`. Remains hermetic — no Cursor Cloud on the default
`northstar review` path.

```bash
# Review a hooks change with the security-hooks intent fixture
$CONTROL/scripts/northstar review --repo "$(pwd)" \
  --diff-file path/to.diff \
  --intent-json $CONTROL/tests/fixtures/code-review/intent-security-hooks.json
```

## Live Agentic Security ingest (M39, opt-in)

After running Cursor `/review-security` (or Security Reviewer Automation), export
the findings JSON and ingest into NorthStar evidence **without** changing the
hermetic default review path:

```bash
# Captain: enable allowlist in the target repo
cp $CONTROL/templates/agent/review/agentic-security-allowlist.yml \
   "$(pwd)/.agent/review/agentic-security-allowlist.yml"
# set enabled: true and ensure owner/repo is listed

$CONTROL/scripts/northstar review ingest-agentic-security \
  --repo "$(pwd)" \
  --artifact path/to/cursor-security-export.json \
  --github-repo owner/name \
  [--run-id my-run] [--outcomes-proposal]
```

Evidence lands at `.agent/evidence/review/<run-id>/agentic-security/`.
Refuse-closed when `enabled: false` or the repo is not listed (M30 posture).
Never auto-merges; never invokes Cursor Cloud from the ingest script.

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

## Finding outcomes (M31)

After humans triage verified findings, record durable Experience lessons (and
optionally a Captain-gated RoutingProposal). Outcomes never originate Captain
approval; proposals are never auto-applied.

```bash
./scripts/record-finding-outcomes.sh \
  --report .agent/evidence/code-review/<run-id>/report.json \
  --triage path/to/triage-outcomes.json \
  --plan-id m31-finding-outcomes-experience \
  --emit-routing-proposal

./scripts/northstar outcomes record \
  --report .agent/evidence/code-review/<run-id>/report.json \
  --triage path/to/triage-outcomes.json \
  --emit-routing-proposal
```

Triage JSON is a list or `{"outcomes":[...]}` with `finding_id`,
`decision` (`accepted`|`rejected`|`deferred`), and optional `label` /
`skill` / `notes`. Accepted/rejected write Experience; deferred stays in
`outcomes.json` only. `--emit-routing-proposal` writes a proposal with
`auto_apply=false`.

## Precision ledger (M33 / B5)

Roll up finding outcomes into a durable precision ledger and dashboard (and
optionally a Captain-gated priority proposal). Precision =
`accepted / (accepted + rejected)`; deferred is counted but excluded from the
denominator. Never auto-applies reputation.

```bash
./scripts/aggregate-precision-ledger.sh \
  --outcomes .agent/evidence/code-review/<run-id>/outcomes.json \
  --ledger-id my-precision-run \
  --emit-priority-proposal

./scripts/northstar precision aggregate \
  --outcomes .agent/evidence/code-review/<run-id>/outcomes.json \
  --outcomes-dir .agent/evidence/code-review \
  --emit-priority-proposal
```

Writes `.agent/evidence/precision/<ledger-id>/precision-ledger.json`,
`dashboard.md`, and `dashboard.json`. `--emit-priority-proposal` refuses unless
at least one skill has decided findings ≥ `--min-sample` (default 5).

## Locks (Captain)

- Hermetic CI — fixture / specialist / heuristic candidates only; no model calls by default
- Default candidates mode: **specialists** (M28)
- Skill slug: `code-reviewer`
- **GitHub draft posting opt-in only** (M30); default remains evidence-only
- **Finding outcomes → Experience are evidence only** (M31); RoutingProposal never auto-applies
- Intent packs are evidence only; Linear never approves
- Tracker: GitHub issues only
- **Repair loop is Captain-gated** (M32 / B4): verified findings only; never auto-merge; default stops at dispatch packet
- **Precision ledger is proposal-only** (M33 / B5): no silent reputation mutation

## Compose with

- `security-review`, `accessibility-review`, `adversarial-reviewer`
- Downstream: `review-fix-loop` consumes verified findings
- Learning loop: `record-finding-outcomes.sh` → Experience → optional RoutingProposal
- Repair: `start-repair-loop.sh` / `northstar repair start` → FIND→PROVE→packet (optional captain-authorized submit prep)
- Precision: `aggregate-precision-ledger.sh` / `northstar precision aggregate` → dashboard + optional priority proposal

## Schemas

- `orchestrator/schemas/code-review-report.schema.json`
- `orchestrator/schemas/intent-pack.schema.json`
- `orchestrator/schemas/finding-outcome.schema.json`
- `orchestrator/schemas/repair-run.schema.json`
- `orchestrator/schemas/precision-ledger.schema.json`
