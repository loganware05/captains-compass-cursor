# Implementation Plan — M47 / Behavior Pattern Learning

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `m47-behavior-pattern-learning` |
| Approved | — |
| Linear | [OVA-59](https://linear.app/ovaltechnologysolutions/issue/OVA-59/m47-behavior-pattern-learning-v1470) · Milestone **M47 — Behavior Pattern Learning** |
| Spec source | [Notion: Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M47 section) |
| Prerequisite | **M46 merged** — PR [#184](https://github.com/loganware05/captains-compass-cursor/pull/184) → `main` @ `cb4f463` (v1.46.0); OVA-58 Done |
| Supersedes | — (consumes M46 behavior ledger; no Policy activation) |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.46.0** @ `cb4f463` |
| Prepared | 2026-10-01 |
| Proposed release | **v1.47.0** (proposal-only patterns; hermetic CI default) |
| Rollback | Tag `rollback/pre-m47-behavior-pattern-learning` @ `cb4f463` (create after approval) |
| Proposed branch | `cursor/m47-behavior-pattern-learning-3192` *(implementation after approval; this PR is plan + M46 closeout)* |
| Captain | Logan Ware |

## Request

After M46 observe-only evaluation, establish **M47 Behavior Pattern Learning**:
detect recurring patterns from the behavior evaluation ledger, group evidence,
and emit **candidate** behavioral guidance — without activating Policies,
mutating prompts/Skills/routing, or granting authority.

## Problem Statement

M46 persists per-execution behavior scores, but NorthStar cannot yet:

1. Detect recurring friction / praise patterns across multiple evaluations
2. Require repeated evidence (not a single bad run) before surfacing a pattern
3. Emit inspectable candidate guidance for later M48–M50 governance
4. Expose a stable `northstar learn` operator surface

Without this, Policy/instruction promotion (M48–M50) has no evidence-backed
pattern layer to consume.

## Desired Outcome

```
.agent/evaluations/behavior/ (M46 ledger)
  → pattern detector (min_occurrence default 3 + quality gates)
  → pattern records + evidence grouping
  → candidate behavioral guidance (proposal-only)
  → northstar learn …
```

No path may activate Policies, mutate Skills/routing/instructions, or set
`approved_for_execution`.

## Decision Summary

| Principle | Implication |
|---|---|
| Proposal only | Patterns / candidates never auto-activate |
| Min occurrence | Default **3** matching evaluations; configurable |
| Sample quality | Prefer non-abstaining, threshold-crossing (or praise) records; configurable |
| Deterministic CI | Pure ledger scan; no network required |
| Separate CLI | `northstar learn` distinct from `evaluate` / `outcomes` |
| Fail closed | Insufficient evidence → no candidate; never mutate authority |
| Builds on M46 | Read dual ledger; do not overload M3 Compass Evaluator |

## Current-State Analysis (live repo @ `cb4f463`)

| Area | Location | M47 use |
|---|---|---|
| Behavior ledger | `orchestrator/behavior/ledger.py`, `.agent/evaluations/behavior/` | Input |
| Signals / thresholds | `orchestrator/behavior/{signals,thresholds}.py` | Grouping keys + quality |
| CLI launcher | `scripts/northstar` (`evaluate` exists; no `learn`) | Add `learn` |
| Skill learning (distinct) | `orchestrator/learning/` Skills loop | **Do not conflate** — behavior patterns are separate |
| Candidate promotion | `orchestrator/promotion/` | Optional later; M47 stays proposal-only |
| Routing proposals | `.agent/routing/proposals/` | Pattern for proposal-only artifacts |

### Capability-plan note

`capability-plan.sh` incorrectly inferred a **frontend/React** workstream.
**Rejected.** M47 is control-plane Python/CLI only.

## Scope

### In (M47)

1. `behavior-pattern.schema.json` (+ optional candidate schema)
2. Deterministic pattern detector over behavior ledger records
3. Configurable `min_occurrence` (default 3) and sample-quality filters
4. Persist under `.agent/evaluations/behavior/patterns/` (JSON + optional index/JSONL)
5. Candidate behavioral guidance objects (proposal-only; `approved_for_execution: false`)
6. `northstar learn` CLI: e.g. `scan`, `list`, `show <pattern-id>`, `export`
7. Enable gate: `COMPASS_BEHAVIOR_LEARN_ENABLED` (default off) **and** explicit CLI — mirror M46 Captain preference unless revised
8. Hermetic fixtures + unit/integration tests
9. Docs: ADR-064, TESTING, PROGRESS, CHANGELOG, VERSION → 1.47.0
10. Evidence under `.agent/evidence/m47-behavior-pattern-learning/`

### Out (Non-Goals)

- Policy / instruction registry or activation (M48–M50)
- Prompt mutation or shadow apply into live agent prompts
- Skill promotion / reputation / routing mutation
- Kimi Project Overseer (M51)
- Replacing DecisionProvider or M46 evaluate
- Auto-writing `.cursor/rules` or Skills from patterns
- Database / Prisma

## Proposed Architecture

```
scripts/northstar learn …
        │
        ▼
scripts/run-behavior-learn.sh
        │
        ▼
orchestrator/behavior/patterns/
  detect.py      # scan ledger → PatternCandidate[]
  store.py       # persist patterns/
  quality.py     # min_occurrence + sample filters
  export.py      # optional CSV/JSON export
        │
        ▼
.agent/evaluations/behavior/patterns/{pattern_id}.json
```

### Pattern key (initial)

Group by: `signal` (+ optional `agent`, `skill_id`, `task_type` if present).
A pattern fires when ≥ `min_occurrence` non-abstaining evaluations have that
signal score ≥ the signal’s threshold (or `praise` ≥ general threshold for
positive patterns).

### Candidate guidance (proposal-only)

```json
{
  "candidate_id": "bcand-...",
  "pattern_id": "bpat-...",
  "kind": "behavioral-guidance",
  "summary": "...",
  "signal": "rework_required",
  "evidence_evaluation_ids": [],
  "approved_for_execution": false,
  "authority_mutation": false
}
```

## Workstreams

| ID | Work |
|---|---|
| WS1 | Pattern + candidate schemas |
| WS2 | Detector + quality gates |
| WS3 | Persistence under `patterns/` |
| WS4 | `northstar learn` CLI + enable flag |
| WS5 | Hermetic tests + fixtures (multi-eval ledger) |
| WS6 | Docs ADR-064 / VERSION 1.47.0 / doctor |

## Files Expected to Change

**New:** `orchestrator/behavior/patterns/`, schemas, `scripts/run-behavior-learn.sh`,
tests/fixtures, docs/plans/M47_…, evidence dir.

**Modify:** `scripts/northstar`, `scripts/doctor.sh`, DECISIONS/TESTING/PROGRESS/CHANGELOG/VERSION,
`docs/integrations/decision-provider.md` (cross-link learn vs evaluate).

## Acceptance Criteria

- [ ] Ledger with ≥3 qualifying evaluations yields a pattern; fewer does not
- [ ] `min_occurrence` configurable; default 3
- [ ] Candidates always `approved_for_execution: false` / `authority_mutation: false`
- [ ] `northstar learn` requires enable flag (if approved) + explicit CLI
- [ ] Hermetic CI; no network; doctor/tests green
- [ ] No Skill/routing/instruction/Policy mutation
- [ ] M46 evaluate paths unchanged and still pass
- [ ] Secrets never enter pattern artifacts

## Testing Strategy

| Layer | What |
|---|---|
| Unit | Detector thresholds, min_occurrence edges, abstain exclusion |
| Integration | `northstar learn scan` over fixture ledger |
| Regression | Skills/routing/evaluate untouched |
| Security | No secret leakage; proposal-only locks |

## Security Review

- Read-only over M46 ledger; redaction inherited from stored packets
- Candidates cannot grant authority
- Enable flag default off

## Accessibility Review

N/A (CLI / control-plane).

## Migration Plan

Additive. Empty patterns dir until first `learn scan`. No backfill required.

## Rollback Plan

1. Unset `COMPASS_BEHAVIOR_LEARN_ENABLED`; stop using `northstar learn`
2. Checkout `rollback/pre-m47-behavior-pattern-learning`
3. Delete `.agent/evaluations/behavior/patterns/` if needed (ledger intact)

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Conflate with Skills learning loop | Separate package path + CLI surface |
| Over-firing on noise | min_occurrence + quality filters |
| Scope creep into M48 | Hard Non-Goals |

## Open Questions (Captain)

1. Confirm enable flag `COMPASS_BEHAVIOR_LEARN_ENABLED` (mirror M46) vs CLI-only?
2. Group patterns by signal only, or also by agent/skill dimensions in M47?
3. Confirm release naming **v1.47.0**?
4. Should positive (`praise`) and negative patterns share one detector with a `polarity` field?

## Assumptions

1. M46 ledger on `main` is the sole input.
2. Proposal-only is sufficient for M47; activation waits for M48–M50.
3. Control repo is the implementation target.

## Definition of Done

M47 complete when NorthStar can scan the behavior ledger, emit evidence-backed
patterns and proposal-only candidates via `northstar learn`, pass validation
with evidence, and grant **no new mutating authority**.

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

## Approval Record

<!-- After Captain approval, record who/when/revision; set Status APPROVED. -->
