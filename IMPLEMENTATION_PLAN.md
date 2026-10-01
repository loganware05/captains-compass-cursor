# Implementation Plan — M49 / Prompt Evaluation Harness

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `m49-prompt-evaluation-harness` |
| Linear | [OVA-61](https://linear.app/ovaltechnologysolutions/issue/OVA-61/m49-prompt-evaluation-harness-v1490) · Milestone **M49 — Prompt Evaluation Harness** |
| Spec source | [Notion: Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M49 section) |
| Notion plan mirror | [M49 Implementation Plan](https://app.notion.com/p/3ece6a901c4381cb8488e32b9b0e6634) |
| Prerequisite | **M48 merged** — PR [#186](https://github.com/loganware05/captains-compass-cursor/pull/186) → `main` @ `2d388cf` (v1.48.0); OVA-60 Done |
| Supersedes | — (consumes M48 bundles; no Policy activation / live prompt injection) |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.48.0** @ `2d388cf` |
| Prepared | 2026-10-01 |
| Proposed release | **v1.49.0** (prompt eval harness; proposal/eval-only; hermetic CI default) |
| Rollback | Tag `rollback/pre-m49-prompt-evaluation-harness` @ `2d388cf` (create after approval) |
| Proposed branch | `cursor/m49-prompt-evaluation-harness-plan-3192` |
| Captain | Logan Ware |

## Request

After M48 instruction registry + PICCO composer, establish **M49 Prompt
Evaluation Harness**: hermetic regression fixtures that compare baseline
instruction/prompt bundles against candidates before any promotion — without
activating Policies, writing live `.cursor/` guidance, or granting authority.

## Problem Statement

M48 can compose baseline vs proposal-inclusive bundles (`include_proposals`),
but NorthStar cannot yet:

1. Run labeled fixture scenarios against baseline vs candidate bundles
2. Score non-regression on instruction adherence, schema validity, hallucinated
   repository state, unnecessary scope, review precision, evidence completeness,
   and approval-boundary compliance
3. Emit a proposal-only comparison report that M50 can consume before promotion
4. Expose a stable operator surface for prompt evaluation

Without this, candidate instructions can only “sound better” — not prove
measurable non-regression before Captain-gated promotion (M50).

## Desired Outcome

```
M48 baseline bundle (include_proposals=False)
  + candidate bundle (include_proposals=True | explicit candidate ids)
  → fixture scenarios under tests/fixtures/behavior/prompt-eval/
  → scored comparison report (proposal-only)
  → northstar prompt-eval …
  → evidence for M50 promotion gates (no activation)
```

No path may activate Policies, mutate `.cursor/rules|skills|agents`, mutate
Skills/routing, or set `approved_for_execution`.

## Decision Summary

| Principle | Implication |
|---|---|
| Eval / proposal only | Reports never auto-promote or activate instructions |
| Separate from behavior evaluate | `northstar evaluate` = run scoring (M46); prompt-eval = instruction non-regression |
| Separate from Compass Evaluator | Do not overload `evaluation.schema.json` (ADR-063 / ADR-065) |
| Baseline fork | Baseline compose forces `include_proposals=False` |
| Hermetic CI | Fixture/file scoring only; no live LLM/Jev in CI |
| Fail closed | Missing fixtures / invalid candidate → fail report; never mutate authority |
| Enable gate | Dual gate (env + explicit CLI), mirroring M46–M48 |

## Open Questions (Captain)

| # | Question | Recommendation |
|---|---|---|
| 1 | CLI surface: top-level `northstar prompt-eval` **or** `northstar instructions eval`? | **`northstar prompt-eval`** — keeps M48 CLI stable; mirrors DecisionProvider eval separation |
| 2 | Enable flag: new `COMPASS_PROMPT_EVAL_ENABLED` **or** reuse `COMPASS_INSTRUCTIONS_ENABLED`? | **New `COMPASS_PROMPT_EVAL_ENABLED`** (default off) — independent gate for eval surface |
| 3 | Scoring mode for v1.49.0: deterministic fixture expectations only **or** also stub DecisionProvider-style signal scoring? | **Deterministic fixtures first** (gold expectations + hash/diff); stub signal scorer optional if cheap |
| 4 | Release naming **v1.49.0** confirmed? | Yes |
| 5 | Persist reports under `.agent/evaluations/behavior/prompt-eval/` **or** only `.agent/evidence/m49-…`? | **Both:** canonical JSON under `…/behavior/prompt-eval/`; summary copy in evidence |

## Scope

### In (M49)

1. `prompt-eval-report.schema.json` — fail-closed (`approved_for_execution: false`, `authority_mutation: false`, `additionalProperties: false`)
2. `orchestrator/behavior/prompt_eval/` — cases loader, baseline/candidate compose, compare, report, service
3. Fixture pack under `tests/fixtures/behavior/prompt-eval/` (mini registry + cases + gold expectations)
4. Metrics (at least): instruction adherence, schema validity, hallucinated repository state, unnecessary scope, verified-review precision, evidence completeness, approval-boundary compliance
5. `northstar prompt-eval` CLI: `run`, `compare`, `export` (exact verbs may trim to `run` + `export` if sufficient)
6. Enable gate: `COMPASS_PROMPT_EVAL_ENABLED` (default off) **and** explicit CLI *(pending Q2)*
7. Persist reports under `.agent/evaluations/behavior/prompt-eval/` *(pending Q5)*
8. Hermetic unit/integration tests (`tests/orchestrator/test_m49_prompt_evaluation_harness.py`)
9. Docs: ADR-066, TESTING, PROGRESS, CHANGELOG, VERSION → 1.49.0
10. Evidence under `.agent/evidence/m49-prompt-evaluation-harness/`
11. Doctor smoke: fail-closed when flag unset

### Out (Non-Goals)

- Policy / instruction activation or shadow apply (M50)
- Live writes to `.cursor/rules|skills|agents`
- Mutating Skills, routing, reputation, or Captain approval
- Live Jev/LLM scoring in CI
- Folding into `northstar evaluate` (behavior ledger) or Compass Evaluator schema
- Project Overseer (M51)
- Database / Prisma / frontend

## Proposed Architecture

```
scripts/northstar prompt-eval …
        │
        ▼
scripts/run-prompt-eval.sh
        │
        ▼
orchestrator/behavior/prompt_eval/
  cases.py / compare.py / report.py / service.py
        │
        ├─► composer.compose_prompt_bundle(include_proposals=False)  # baseline
        └─► composer.compose_prompt_bundle(include_proposals=True)   # candidate
        │
        ▼
.agent/evaluations/behavior/prompt-eval/<report-id>.json
(+ evidence summary under .agent/evidence/m49-prompt-evaluation-harness/)
```

### Scoring model (hermetic)

Reuse patterns from:

- `orchestrator/providers/decision/eval.py` — labeled cases + wrong/missed metrics
- DecisionProvider shadow — baseline vs candidate disagreement (evidence only)
- Precision ledger — aggregate labeled outcomes without auto-apply

Each fixture case supplies:

- context (`agent`, `skill_id`, `task_type`, `model_hint`)
- optional candidate instruction ids / proposal fixtures
- gold expectations (must-pass properties + allowed regressions)

Compare produces per-case deltas and an aggregate `non_regression: pass|fail`.

## Files to Add / Modify

### Add

| Path | Purpose |
|---|---|
| `orchestrator/behavior/prompt_eval/__init__.py` | Package |
| `orchestrator/behavior/prompt_eval/cases.py` | Load fixture cases |
| `orchestrator/behavior/prompt_eval/compare.py` | Baseline vs candidate compare |
| `orchestrator/behavior/prompt_eval/report.py` | Persist / validate report |
| `orchestrator/behavior/prompt_eval/service.py` | CLI service layer |
| `orchestrator/schemas/prompt-eval-report.schema.json` | Report contract |
| `tests/fixtures/behavior/prompt-eval/` | Mini registry + cases |
| `scripts/run-prompt-eval.sh` | Enable-gated runner |
| `tests/orchestrator/test_m49_prompt_evaluation_harness.py` | Hermetic tests |
| `docs/plans/M49_PROMPT_EVALUATION_HARNESS.md` | Plan archive |
| `.agent/budgets/m49-prompt-evaluation-harness.md` | Autonomy budget |
| `.agent/evidence/m49-prompt-evaluation-harness/` | Validation evidence |

### Modify (thin)

| Path | Change |
|---|---|
| `orchestrator/behavior/enabled.py` | `prompt_eval_enabled()` / `require_prompt_eval_enabled()` |
| `scripts/northstar` | Dispatch `prompt-eval` |
| `scripts/doctor.sh` | Fail-closed smoke when unset |
| `orchestrator/schemas/validate.py` | Register report schema |
| `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md`, `VERSION` | M49 docs/release |
| Optional thin: `composer.py` | Document/export baseline helper if needed (flag already exists) |

### Explicit non-touch

- No M50 Policy promotion / `.cursor/` writes
- No changes to M46 evaluate authority boundaries
- No live provider keys in fixtures

## Acceptance Criteria

- [ ] Harness composes baseline (`include_proposals=False`) vs candidate bundles
- [ ] Fixture cases score the listed non-regression properties hermetically
- [ ] Report schema rejects `approved_for_execution: true` / authority mutation
- [ ] `northstar prompt-eval` requires enable flag + explicit CLI
- [ ] No write to `.cursor/rules|skills|agents`; no Skill/routing/Policy activation
- [ ] No live LLM/Jev required for CI
- [ ] M46 evaluate + M47 learn + M48 instructions paths still pass
- [ ] Doctor/tests green; secrets never enter reports
- [ ] Evidence + ADR-066 + VERSION 1.49.0

## Test Matrix

| Layer | Coverage |
|---|---|
| Unit | Case load, hash/diff compare, schema reject, enable gate |
| Integration | CLI `run` / `export` against fixture registry |
| Regression | Existing M46/M47/M48 suites unchanged |
| Security | No `.cursor/` writes; fail-closed gates; redaction |
| Doctor | Flag unset → prompt-eval unavailable |

## Rollback Plan

1. Unset `COMPASS_PROMPT_EVAL_ENABLED`; stop using `northstar prompt-eval`
2. Checkout `rollback/pre-m49-prompt-evaluation-harness`
3. Delete `.agent/evaluations/behavior/prompt-eval/` if needed (M46–M48 artifacts intact)

## Migration Impact

- Additive only; default-off gate
- No database / schema migrations
- Existing instruction registry layout unchanged

## Security Considerations

- Proposal-only report schema (`additionalProperties: false`)
- Fail closed on missing/invalid inputs
- No secrets in fixture packs or reports (reuse `redact_text`)
- No authority or live-prompt mutation paths

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Please answer open questions 1–5 (or accept recommendations) with approval.

## Approval Record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Approval text | — |
| Approved revision | — |
