# Implementation Plan — M54 / Behavior Loop Operator Closure

## Metadata

- Status: APPROVED

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m54-behavior-loop-closure` |
| Approved | 2026-10-11 — Captain: "I approve" (accepts recommended decisions 1–6) |
| Linear | [OVA-70](https://linear.app/ovaltechnologysolutions/issue/OVA-70/m54-behavior-loop-operator-closure-v1590) · Project **P-OVA-4** |
| Spec source | [Notion: Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) — closeout of provenance + exemplars + Overseer |
| Notion plan mirror | [M54 Implementation Plan](https://app.notion.com/p/3f7e6a901c4381f1a2bcfa0335f8aa1a) |
| Prerequisite | **M53 merged** — PR [#196](https://github.com/loganware05/captains-compass-cursor/pull/196) → **v1.58.0** @ `47f3241`; OVA-69 Done |
| Supersedes | Completed plan `m53-prompt-policy-provenance` |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.58.0** @ `47f3241` |
| Prepared | 2026-10-11 |
| Proposed release | **v1.59.0** |
| Rollback | Tag `rollback/pre-m54-behavior-loop-closure` @ `47f3241` |
| Proposed branch | `feature/OVA-70-m54-behavior-loop-closure` |
| Capability plan | `.agent/plans/m54-behavior-loop-closure/` |
| Captain | Logan Ware |

## Request

Continue after M53. The Behavioral Intelligence Loop sprint (M46–M53) has
shipped its core surfaces. Close the loop by **connecting** provenance,
exemplars, prompt-eval, and Overseer status — without opening AHF-P07 or
granting new mutating authority.

## Current state (evidence)

| Track | Reality |
|---|---|
| M46–M53 | Shipped through **v1.58.0** (#196 on `main` @ `47f3241`) |
| Provenance | Ledger + CLI gated; evaluate emit works; compose path not wired |
| Exemplars | Draft/list under `.agent/examples/`; not consumed by prompt-eval |
| Prompt-eval | Hermetic `tests/fixtures/behavior/prompt-eval/cases.json` only |
| Status / Overseer | Snapshot/explain/compare; no provenance refs in status artifacts |
| AHF-P07 | Still deferred / gated |
| Scheduled Overseer | Still deferred (M52/M53 non-goal) |

## Problem Statement

Operators can create exemplars and provenance records, but cannot yet:

1. Feed curated exemplars into the prompt-eval harness as optional cases
2. Capture provenance from compose when an `execution_id` is available
3. See provenance pointers when using `northstar status` explain/compare
4. Formally close P-OVA-4 after the last sprint wiring lands

## Desired Outcome

```
.agent/examples/{positive,negative}/
  → optional prompt-eval cases (read-only load; never auto-promote)
compose (+ optional execution_id) + COMPASS_PROVENANCE_ENABLED
  → best-effort provenance record
northstar status explain|compare
  → provenance_refs[] in snapshot/artifacts (read-only)
docs + Linear P-OVA-4 closeout after merge
```

No path may approve plans, promote Skills/Policies, alter routing, merge,
deploy, schedule unsupervised Overseer jobs, or enable live trading.

## Decision Summary (recommended)

| # | Decision | Recommendation |
|---|---|---|
| 1 | Scope | **Operator closure wiring** (exemplars→prompt-eval, compose provenance, status refs, sprint closeout) — not AHF-P07 |
| 2 | Exemplar load | Opt-in flag `COMPASS_PROMPT_EVAL_INCLUDE_EXEMPLARS=1` (default off); only schema-valid drafts; never write Skills/Policies |
| 3 | Compose provenance | Best-effort when gated **and** `execution_id` provided / discoverable; missing id → skip (no fail) |
| 4 | Status refs | Append read-only `provenance_refs` (ids + paths) under `.agent/status/` artifacts only |
| 5 | Scheduled Overseer | **Defer** again (no GHA cron in M54) unless Captain opts in below |
| 6 | Release | **v1.59.0**; mark P-OVA-4 complete after merge |

### Alternate tracks (Captain may choose instead)

| Alt | Scope | Notes |
|---|---|---|
| A | **AHF-P07 paper-only** deeper on-chain metric family | Separate plan; stays research/paper; readiness still deny-by-default |
| B | **Opt-in scheduled Overseer** (GHA) | Explicit cron + `COMPASS_STATUS_ENABLED`; still no authority mutation |

## Resolved Decisions (Captain — 2026-10-11)

| # | Decision |
|---|---|
| 1 | Operator closure wiring (not AHF-P07) |
| 2 | Opt-in `COMPASS_PROMPT_EVAL_INCLUDE_EXEMPLARS` |
| 3 | Compose provenance when gated + execution_id |
| 4 | Status provenance_refs (read-only) |
| 5 | Defer scheduled Overseer |
| 6 | Release **v1.59.0** |

## Approval Record

Captain Logan Ware — 2026-10-11 — "I approve" (recommended decisions 1–6 accepted).

## Scope

### In (M54)

1. Prompt-eval: optional loader mapping exemplar polarity → `expect_non_regression` pass/fail cases; hermetic fixtures remain default CI path
2. Instructions compose: optional `--execution-id` (or env) for best-effort provenance capture when gated
3. Status explain/compare: include recent provenance refs (bounded list) when provenance store non-empty; never mutate authority
4. Hermetic tests + doctor smokes for new flags / fail-closed defaults
5. Docs: ADR-076, TESTING, PROGRESS, PROJECT_CONTEXT, CHANGELOG, VERSION → 1.59.0
6. Evidence under `.agent/evidence/m54-behavior-loop-closure/`
7. After merge: mark Linear project P-OVA-4 complete; Notion sprint mirrors COMPLETE

### Out (Non-Goals)

- Auto-activating Policies or rewriting Skills from exemplars
- AHF-P07 / live broker / wallet signing
- GitHub Actions scheduled Overseer (unless Captain selects Alt B)
- Requiring exemplars for CI green
- Changing Captain approval boundary

## Proposed Architecture

```
northstar prompt-eval run  (+ COMPASS_PROMPT_EVAL_INCLUDE_EXEMPLARS=1)
        │
        ▼
load cases.json  ∪  map exemplars → PromptEvalCase (temp only)
        │
northstar instructions compose --execution-id … (+ COMPASS_PROVENANCE_ENABLED)
        │
        ▼
capture_from_execution (best-effort)
        │
northstar status explain
        │
        ▼
snapshot + provenance_refs[] under .agent/status/ only
```

## Capability / Agent Plan (adjusted)

Generic capability graph may suggest Docker — **override** toward
behavior/orchestrator/status Skills; no Docker/frontend.

| Task | Profile | Notes |
|---|---|---|
| discovery | `repository-scout` | Locate prompt_eval/cases, compose, status seams |
| architecture | `architecture-agent` | Exemplar→case mapping + status refs contract |
| implementation | `implementation-agent` | Thin wiring only |
| validation | `test-engineer` | Hermetic tests + doctor |
| documentation | `documentation-agent` | ADR/PROGRESS/VERSION + sprint closeout |

Machine artifacts: `.agent/plans/m54-behavior-loop-closure/`.

## Files to Add / Modify

### Add

| Path | Purpose |
|---|---|
| `orchestrator/behavior/prompt_eval/exemplars.py` (or extend `cases.py`) | Map exemplars → cases |
| `tests/orchestrator/test_m54_behavior_loop_closure.py` | Hermetic tests |
| `docs/plans/M54_BEHAVIOR_LOOP_CLOSURE.md` | Plan archive |
| `.agent/budgets/m54-behavior-loop-closure.md` | Autonomy budget |
| `.agent/evidence/m54-behavior-loop-closure/` | Validation evidence |

### Modify (thin)

| Path | Change |
|---|---|
| `orchestrator/behavior/prompt_eval/*` | Optional exemplar include |
| `orchestrator/behavior/instructions/service.py` + CLI | Optional execution_id → provenance |
| `orchestrator/status/*` | provenance_refs on explain/compare |
| `scripts/northstar` / doctor | Flags + smokes |
| Docs / VERSION | M54 release memory |

## Acceptance Criteria

- [x] Exemplars optionally load into prompt-eval; default CI path unchanged
- [x] Compose can emit provenance when gated + execution_id present
- [x] Status explain/compare surfaces bounded provenance refs (read-only)
- [x] Schemas / gates still reject authority mutation and auto_promoted true
- [x] Doctor/tests green; no live providers required
- [x] Evidence + ADR-076 + VERSION 1.59.0
- [x] Linear OVA-70 linked; P-OVA-4 closeout after merge

## Test Matrix

| Layer | Coverage |
|---|---|
| Unit | Exemplar→case mapping; compose skip without execution_id; status refs empty-ok |
| Integration | CLI prompt-eval with include flag; provenance capture from compose |
| Regression | M46–M53 suites green; default prompt-eval without exemplars |
| Security | Fail-closed defaults; no secrets in status/provenance |
| Doctor | New flags unset → prior behavior |

## Rollback Plan

1. Tag `rollback/pre-m54-behavior-loop-closure` @ `47f3241` after approval
2. Revert M54 PR / reset to tag
3. VERSION / docs roll back with the revert

## Autonomy Budget

| Limit | Value |
|---|---|
| Max iterations | 8 |
| Max wall time | 4 hours |
| Stop on | Illegal authority mutation, secret leakage, budget exhaustion |

Track in `.agent/budgets/m54-behavior-loop-closure.md`.

## Security Considerations

- Exemplar include is opt-in and read-only
- Provenance / status writes stay under `.agent/` only
- Never auto-promote or rewrite `.cursor/skills`
- AHF / live execution remain denied

## Approval Boundary

**Approved.** Implementation may proceed on `feature/OVA-70-m54-behavior-loop-closure`
with rollback `rollback/pre-m54-behavior-loop-closure` @ `47f3241`.
