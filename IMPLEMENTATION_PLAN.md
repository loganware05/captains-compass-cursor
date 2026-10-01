# Implementation Plan — M46 / Behavior Intelligence Foundation

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m46-behavior-intelligence-foundation` |
| Approved | 2026-10-01 — Captain: "I approve" |
| Linear | [OVA-58](https://linear.app/ovaltechnologysolutions/issue/OVA-58/m46-behavior-intelligence-foundation-v1460) · Project [P-OVA-4](https://linear.app/ovaltechnologysolutions/project/northstar-behavioral-intelligence-loop-e24174b3f1ef) · Milestone **M46 — Behavior Intelligence Foundation** |
| Spec source | [Notion: NorthStar Behavioral Intelligence Loop — Sprint Development Plan](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (fetched 2026-09-30) |
| Notion plan mirror | [M46 Implementation Plan (Notion)](https://app.notion.com/p/3ece6a901c4381a0826dcc5e553daa40) |
| Supersedes | — (builds on M41–M45 DecisionProvider; new **observation-only** behavior surface) |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.45.0** @ `0d125c7` (post-M45 #183) |
| Prepared | 2026-09-30 |
| Last updated | 2026-10-01 — Captain resolved open questions |
| Release | **v1.46.0** (confirmed; observe-only; hermetic CI default) |
| Rollback | Tag `rollback/pre-m46-behavior-intelligence` @ `0d125c7` (create after approval) |
| Proposed branch | `cursor/m46-behavior-intelligence-foundation-3192` *(implementation branch after approval; this PR is plan-only)* |
| Captain | Logan Ware |
| Pinned model | **`jev-1.13.0`** (reuse DecisionProvider pin; no unpinning) |

## Request

Establish **M46 Behavior Intelligence Foundation**: observation, evaluation,
persistence, and operator inspection for completed engineering executions —
without granting any new mutating authority over prompts, Skills, Policies,
routing, reputation, approval state, or repository contents.

This is the first milestone of the Notion Behavioral Intelligence Loop sprint.
Jarvis feedback-mining ideas are absorbed into NorthStar’s existing
DecisionProvider / Experience / telemetry / governance architecture — **not**
as a parallel subsystem.

## Problem Statement

NorthStar already records ExecutionRuns, Experience, review findings, and
DecisionProvider shadows (skills / review / agent routing), but it cannot yet:

1. Normalize a completed execution into a **bounded behavior-evaluation packet**
2. Score engineering-friction / behavior signals through stub or Jev
3. Persist a reproducible **behavior evaluation ledger**
4. Expose a stable `northstar evaluate` operator surface

Without this foundation, later milestones (pattern learning, instruction
registry, policy promotion, Project Overseer) have nothing governed to learn
from.

## Desired Outcome

After M46, NorthStar can:

```
ExecutionRun (+ plan / evidence / review refs)
  → bounded evaluation packet
  → stub | file | jev DecisionProvider.evaluate_behavior
  → .agent/evaluations/behavior/ ledger (JSON/JSONL + schema)
  → northstar evaluate …
```

…and **none** of those steps may mutate routing, Skills, instructions,
reputation, approval gates, or authority.

## Decision Summary

| Principle | Implication |
|---|---|
| Observe only | No prompt / Policy / Skill / routing / reputation mutation in M46 |
| Separate object | New `behavior-evaluation` schema — **do not overload** existing Compass Evaluator `evaluation.schema.json` |
| Nested ledger | Persist under `.agent/evaluations/behavior/` so M3 experiment JSON files stay undisturbed |
| Dual ledger formats | Per-record JSON files **and** append-only `ledger.jsonl` (both canonical; keep in sync) |
| Enable flag | `COMPASS_BEHAVIOR_EVAL_ENABLED` required (default off) **in addition to** explicit CLI |
| DecisionProvider | Add `evaluate_behavior` beside `suggest_skills` / `triage_review` / `suggest_agents` |
| Fail closed | Abstain / error / malformed / stub → no ledger false-positives that grant authority; never mutate |
| Hermetic CI | Default stub provider + behavior-eval flag unset; no network |
| Compact packets | Diff metadata + evidence refs + plan refs — not full repo / secrets / raw tool dumps |
| Thresholds configurable | General 0.70; stricter floors for security / boundary (reviewable config) |
| Captain authority | `IMPLEMENTATION_PLAN.md` approval gate unchanged |

## Current-State Analysis (live repo — authoritative)

Inspected on `main` @ `0d125c7` (v1.45.0):

| Area | Live location | M46 implication |
|---|---|---|
| DecisionProvider protocol | `orchestrator/providers/decision/__init__.py` | Extend with `evaluate_behavior` |
| Types / question revisions | `orchestrator/providers/decision/types.py`, `questions/*.json` | Add `behavior_eval_v1` + request/result types |
| Stub / file / jev adapters | `file_provider.py`, `jev_provider.py`, stub in `__init__.py` | Implement new method; fail-closed |
| Existing Decision eval harness | `orchestrator/providers/decision/eval.py` | Keep for skill-suggestion offline eval; do **not** conflate with behavior ledger |
| Compass Evaluator (M3) | `orchestrator/evaluator/record.py`, `schemas/evaluation.schema.json`, `.agent/evaluations/{id}.json` | **Leave intact**; nest behavior ledger under `.agent/evaluations/behavior/` |
| Execution telemetry | `orchestrator/telemetry/{record,store}.py`, `.agent/runs/`, `execution-run.schema.json` | Primary input source for packets |
| Experience | `.agent/experience/`, `experience.schema.json` | Optional linked evidence |
| Review / repair / outcomes | `scripts/run-code-review.sh`, `record-finding-outcomes.sh`, repair loop | Optional verified-finding + repair refs in packets |
| Operator CLI | `scripts/northstar` (`skills\|review\|intent\|outcomes\|repair\|precision\|context`) | Add `evaluate` surface + thin wrapper script |
| Doctor | Expects `.agent/evaluations/.gitkeep` | Extend checks for behavior schema / layout without breaking M3 |
| Secrets | `COMPASS_JEV_API_KEY` / `TYPESAFE_API_KEY` | Reuse; **never** add `jarvis-key.txt` or committed secrets |

**Naming collision to avoid:** `orchestrator/evaluator/` + `evaluation.schema.json` mean *bounded alternative-comparison experiments*, not behavior scoring. M46 uses distinct names (`behavior_evaluation`, `behavior-evaluation.schema.json`, package `orchestrator/behavior/` or similar).

### Capability-plan note

`./scripts/capability-plan.sh --plan-id m46-behavior-intelligence-foundation` was run.
Machine artifacts: `.agent/plans/m46-behavior-intelligence-foundation/{resolve,task-graph,manifests}.json`.

The auto task graph incorrectly inferred a **Prisma/database** workstream from
generic “schema” language. **That workstream is rejected.** M46 has no database
migrations. Human workstreams below supersede the machine graph for execution.

## Scope

### In (M46)

1. Versioned `behavior-evaluation` JSON schema + signal definitions
2. Evaluation packet normalizer (ExecutionRun → bounded packet)
3. DecisionProvider `evaluate_behavior` on stub / file / jev
4. Persistence: `.agent/evaluations/behavior/` — **both** per-record `{evaluation_id}.json` **and** append-only `ledger.jsonl`
5. Threshold config (general / security / boundary)
6. `northstar evaluate` CLI gated by `COMPASS_BEHAVIOR_EVAL_ENABLED`: `pending`, `run`, `review`, `retry`, `export`
7. Hermetic fixtures + unit/integration tests
8. Provenance fields (repo SHA, NorthStar version, provider/model, schema version, optional prompt_bundle_hash)
9. Docs: ADR, TESTING, PROGRESS, CHANGELOG, decision-provider integration, VERSION → 1.46.0
10. Evidence under `.agent/evidence/m46-behavior-intelligence-foundation/`

### Out (explicit Non-Goals)

- Automatic prompt / Policy / instruction mutation (M48–M50)
- Pattern learning / `northstar learn` (M47)
- Skill promotion or reputation mutation
- Agent-routing mutation / APPLY for behavior
- Kimi K3 Project Overseer / `northstar status` (M51)
- Replacing deterministic baselines with Jev
- Weakening Captain approval gate
- CSV as canonical store (export only)
- Parallel “Jarvis” subsystem or committed API key files
- Database / Prisma of any kind

## Proposed Architecture

```
scripts/northstar evaluate …
        │
        ▼
scripts/run-behavior-evaluate.sh  (thin CLI)
        │
        ▼
orchestrator/behavior/
  packet.py      # normalize ExecutionRun + evidence refs → BehaviorEvalPacket
  ledger.py      # append/load idempotent records under .agent/evaluations/behavior/
  thresholds.py  # load configurable floors
  export.py      # CSV export (non-canonical)
        │
        ▼
DecisionProvider.evaluate_behavior(packet)
  stub → abstain / deterministic fixture scores
  file → offline fixtures
  jev  → behavior_eval_v1 questions → signal probabilities
        │
        ▼
behavior-evaluation record (schema-valid) → ledger
```

### Initial signal set (definitions required in schema/docs)

**Jarvis-derived:** `wrong_answer`, `ignored_instruction`, `format_violation`,
`hedging`, `repeated_request`, `praise`

**Engineering-specific:** `unnecessary_scope`, `hallucinated_repository_state`,
`unverified_claim`, `tool_misuse`, `boundary_violation`, `weak_test_coverage`,
`test_workaround`, `unsafe_git_operation`, `excessive_context`,
`unnecessary_abstraction`, `missing_evidence`, `rework_required`

**Canonical signals include all of the above plus `weak_verification`** (Notion
packet example). `weak_verification`, `weak_test_coverage`, and
`unverified_claim` are **distinct** — not aliases.

### Threshold defaults (config, not hard-coded sole constant)

```yaml
evaluation:
  thresholds:
    general: 0.70
    security: 0.50
    boundary_violation: 0.40
```

Threshold changes are reviewable config diffs; M46 does not auto-act on crossings
beyond recording / CLI review display.

### Env contract additions

| Variable | Default | Meaning |
|---|---|---|
| *(reuse)* `COMPASS_DECISION_PROVIDER` | `stub` | stub \| file \| jev |
| `COMPASS_BEHAVIOR_EVAL_ENABLED` | unset/off | **Required** for `northstar evaluate` to run (Captain: flag + CLI) |
| `COMPASS_BEHAVIOR_EVAL_THRESHOLDS` | path or inline defaults | Optional override path |

CLI alone is insufficient: operators must set `COMPASS_BEHAVIOR_EVAL_ENABLED=1`
**and** invoke `northstar evaluate …`. Unset flag → CLI exits non-zero with a
clear message; CI stays bit-identical.

## Workstreams

| ID | Work | Files (expected) |
|---|---|---|
| WS1 | Schema + signal definitions + threshold config | `orchestrator/schemas/behavior-evaluation.schema.json`; signal glossary doc; config defaults |
| WS2 | Packet normalizer | `orchestrator/behavior/packet.py`; reuse telemetry loaders; optional review/outcome refs |
| WS3 | DecisionProvider `evaluate_behavior` | `types.py`, `__init__.py`, `file_provider.py`, `jev_provider.py`, `questions/behavior_eval_v1.json` |
| WS4 | Ledger persistence | `orchestrator/behavior/ledger.py`; `.agent/evaluations/behavior/` layout; idempotency |
| WS5 | CLI | `scripts/run-behavior-evaluate.sh`; `scripts/northstar` `evaluate` dispatch + help locks |
| WS6 | Tests + fixtures | `tests/orchestrator/test_m46_*.py`; fixtures under `tests/fixtures/behavior/` |
| WS7 | Docs / VERSION / doctor | ADR-063; TESTING; PROGRESS; CHANGELOG; `docs/integrations/decision-provider.md`; doctor layout check; VERSION 1.46.0 |

Parallelizable after WS1: WS2 ∥ WS3; then WS4 depends on both; WS5 after WS4; WS6 continuous; WS7 last.

## Files Expected to Change

**New**

- `orchestrator/behavior/` (`__init__.py`, `packet.py`, `ledger.py`, `thresholds.py`, `export.py`)
- `orchestrator/schemas/behavior-evaluation.schema.json`
- `orchestrator/providers/decision/questions/behavior_eval_v1.json`
- `scripts/run-behavior-evaluate.sh`
- `tests/orchestrator/test_m46_behavior_evaluation.py` (+ fixtures)
- `docs/plans/M46_BEHAVIOR_INTELLIGENCE_FOUNDATION.md`
- `.agent/evidence/m46-behavior-intelligence-foundation/`
- `.agent/evaluations/behavior/.gitkeep` (+ optional `schemas/` copy or symlink policy)

**Modify**

- `orchestrator/providers/decision/{__init__.py,types.py,file_provider.py,jev_provider.py}`
- `scripts/northstar`
- `scripts/doctor.sh` (behavior layout / schema presence)
- `docs/integrations/decision-provider.md`
- `DECISIONS.md` (ADR-063)
- `TESTING.md`, `PROGRESS.md`, `CHANGELOG.md`, `VERSION`
- `IMPLEMENTATION_PLAN.md` (this file → APPROVED after Captain sign-off)

**Do not modify for M46:** matcher rankings, APPLY/shadow skill/review/agent
routing semantics, repair auto-merge locks, installer overwrite policy (beyond
doctor/layout if required).

## Acceptance Criteria

- [ ] Completed ExecutionRuns normalize into schema-valid evaluation packets
- [ ] Stub/file providers evaluate hermetically in CI (no network)
- [ ] Jev path exists via DecisionProvider abstraction (Captain-local; not CI-required)
- [ ] Invalid / abstaining / errored provider output fails closed; no authority mutation
- [ ] Records persist under `.agent/evaluations/behavior/` with provenance
- [ ] Re-run finalized evaluation is idempotent or explicitly versioned
- [ ] `northstar evaluate` subcommands documented and tested
- [ ] CSV export does not become canonical store
- [ ] Existing doctor / tests / DecisionProvider M41–M45 flows remain green
- [ ] No evaluation path mutates routing, Skills, instructions, reputation, or approval state
- [ ] Secrets never enter committed artifacts
- [ ] Existing M3 Compass Evaluator (`evaluation.schema.json` / `{eid}.json`) untouched in behavior

## Testing Strategy

| Layer | What |
|---|---|
| Unit | Schema accept/reject; stub scores; threshold boundaries; idempotent ledger write; packet with missing optional evidence |
| Provider | Malformed output; timeout/failure; abstention; file fixtures; roster/packet bounds |
| Integration | `northstar evaluate run <execution-id>` against fixture ExecutionRun |
| Regression | Assert no mutation of routing / skill lists / instruction files; CI provider stub |
| Structural | doctor layout; VERSION; help text locks |
| Security | No secrets in packets/ledger; no jarvis-key file; Jev allowlist URL/model unchanged |
| Evidence | `.agent/evidence/m46-behavior-intelligence-foundation/` (test logs, sample ledger excerpt, CLI help) |

Commands (post-approval):

```bash
./scripts/doctor.sh
./tests/run.sh
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_m46_*.py' -v
./scripts/northstar evaluate run <execution-id> --repo .
```

## Security Review

- Reuse existing Jev credential env vars; refuse committed key files
- Packets carry path/ID refs and compact metadata only — no raw secrets, full diffs of secret-bearing files, or unfiltered tool transcripts
- Fail closed on provider errors
- Behavior evaluation never sets `approved_for_execution`, never promotes, never merges

## Accessibility Review

N/A (CLI / schema / control-plane; no UI).

## Migration Plan

- Additive only. Existing `.agent/evaluations/*.json` M3 records remain valid.
- New subdirectory `.agent/evaluations/behavior/` created on first write / installer-doctor expectation.
- No data backfill required for M46 (evaluate pending may skip incomplete runs).

## Deployment Plan

- Control-repo release **v1.46.0** after merge
- Product repos pick up via `update.sh` when Captain chooses
- Live Jev evaluation remains Captain-local opt-in

## Rollback Plan

1. Unset any behavior-eval enable flags; stop using `northstar evaluate`
2. Revert merge / checkout `rollback/pre-m46-behavior-intelligence`
3. Delete `.agent/evaluations/behavior/` ledger if needed (non-destructive to M3 evaluations)
4. CI remains green on stub provider regardless

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Name collision with M3 Evaluator | Distinct schema/package/paths; docs call out separation |
| Over-broad packets leak secrets | Compact normalizer + schema denylist tests |
| Capability planner invents DB work | Explicit rejection in this plan |
| Scope creep into M47–M51 | Hard Non-Goals; stop at observe/persist/CLI |
| Jev flakiness | Fail closed; hermetic stub/file for CI |

## Required Capabilities

Inferred (human-curated from resolve + repo): schema design, DecisionProvider
extension, telemetry integration, CLI operator surface, hermetic testing,
security review, documentation.

## Reusable Capabilities Found

- DecisionProvider stub/file/jev pattern (M41–M45)
- Telemetry ExecutionRun store
- Experience / finding-outcome evidence refs
- `scripts/northstar` launcher topology
- Schema validation via `orchestrator/schemas/validate.py`
- Autonomy budget + evidence matrix conventions

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — none queried (TI stub).

## Task Graph (human-corrected)

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| `task-discovery` | Confirm integration points (done in this plan) | — | no |
| `task-architecture` | Finalize schema + package boundaries | task-discovery | no |
| `task-impl-core` | Packet + provider + ledger + CLI | task-architecture | no (internal WS parallel OK) |
| `task-validation` | Unit/integration/doctor/regression | task-impl-core | no |
| `task-security-review` | Secrets / fail-closed / authority locks | task-impl-core | yes |
| `task-documentation` | ADR/TESTING/PROGRESS/CHANGELOG/VERSION | task-validation, task-security-review | no |

Machine artifacts remain under `.agent/plans/m46-behavior-intelligence-foundation/` for audit; **ignore** `task-impl-database`.

## Proposed Agent Configuration

| Task | Profile | Notes |
|---|---|---|
| discovery / architecture | First Mate + architecture-agent | Plan authoring (this document) |
| impl-core | implementation-agent | Python orchestrator + bash CLI |
| validation | test-engineer | Hermetic unittest + doctor |
| security | security-reviewer | Packet/secret/authority |
| documentation | documentation-agent | Memory docs |

## Evaluation Strategy

- Acceptance criteria checklist above
- Adversarial review after implementation
- Compare hermetic stub fixtures (positive + negative exemplars) for stability
- No live-Jev CI gate

## Learning Plan

Retain plan artifacts; after merge record ExecutionRun + (dogfood) behavior
evaluation of the M46 workstream itself under evidence — without promoting any
Policy.

## Autonomy Budget

After approval, create `.agent/budgets/m46-behavior-intelligence-foundation.md`:

| Limit | Proposed |
|---|---|
| Max iterations | 12 |
| Max failed validation cycles | 3 |
| Max estimated cost | Captain-set |
| Max elapsed time | Captain-set |
| On limit | Budget Stop Report under `.agent/evidence/m46-behavior-intelligence-foundation/` |

## Assumptions

1. Control repo (`captains-compass-cursor`) is the implementation target for M46.
2. Notion sprint page is architectural intent; live paths above win on conflict.
3. Captain wants observe-only foundation before M47+ learning.
4. `jev-1.13.0` pin remains; OPENROUTER is not required if Typesafe key path works.
5. Sandbox repo is out of scope unless Captain requests a dogfood install after merge.

## Resolved Decisions (Captain — 2026-10-01)

| # | Decision |
|---|---|
| 1 | **Both:** `COMPASS_BEHAVIOR_EVAL_ENABLED` (default off) **and** explicit `northstar evaluate` CLI |
| 2 | **Both** ledger formats: per-record JSON + append-only `ledger.jsonl` |
| 3 | Create Linear issue now; create Linear project + M46–M51 sprint milestone now |
| 4 | Release naming **confirmed: v1.46.0** |
| 5 | Keep `weak_verification` as a distinct canonical signal alongside `weak_test_coverage` and `unverified_claim` (not aliases) |

## Definition of Done

M46 is complete when NorthStar can observe a completed engineering execution,
build a bounded evidence-backed evaluation packet, evaluate via stub or Jev
through DecisionProvider, persist a reproducible behavior record, expose it via
`northstar evaluate`, pass applicable validation with evidence, update memory
docs — and grant the evaluation system **no new mutating authority**.

## Post-M46 Roadmap (context only — not this plan)

| Milestone | Intent |
|---|---|
| M47 | Behavior pattern learning |
| M48 | Instruction registry + prompt composer |
| M49 | Prompt evaluation harness |
| M50 | Policy / instruction promotion lifecycle |
| M51 | Kimi K3 Project Overseer (`northstar status`) |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Machine-generated capability matches and agent manifests are proposals only.
This cloud turn produces **plan documentation only** (no product implementation).

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-01 |
| Approval text | "I approve" |
| Approved revision | plan with Captain-resolved open questions (OVA-58, Notion mirror) |
