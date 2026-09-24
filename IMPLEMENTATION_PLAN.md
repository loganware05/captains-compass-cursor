# Implementation Plan — M43 / Jev Decision Service (Ranking Enablement)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m43-jev-ranking-enablement` |
| Approved | 2026-09-24 (Captain) |
| Linear | [OVA-55](https://linear.app/ovaltechnologysolutions/issue/OVA-55/m43-jev-decisionprovider-ranking-enablement-v1430) |
| Supersedes | Plan draft on PR #181; builds on M41 ADR-058 |
| Product | **NorthStar** |
| Baseline | **v1.42.0** @ `ed20499` (rebaseline to post-M42 `main` if #180 merges first) |
| Prepared | 2026-09-24 |
| Spec source | Captain approval + open-question resolutions; ADR-058; `docs/integrations/decision-provider.md` |
| Proposed release | **v1.43.0** (default-off) |
| Rollback | Tag `rollback/pre-m43-jev-ranking-enablement` at pre-implementation `main` |
| Branch | `cursor/m43-jev-ranking-enablement-753c` |
| Captain | Logan Ware |
| Pinned model | **`jev-1.13.0`** |

## Request

Opt-in, thresholded **ranking enablement**: allow DecisionProvider suggestions to
mutate `recommended_skill_ids` when `COMPASS_DECISION_APPLY=1` and confidence
gates pass — without bypassing eligibility or any Captain authority. CI/default
remain matcher-only.

## Problem

M41 shadow compares Jev/file suggestions to the matcher but never changes
dispatch. Captain ordered ranking enablement next. Applying without thresholds,
eligibility re-checks, and a holdout gate risks wrong skill loads.

## Decision summary

| Principle | Implication |
|---|---|
| Opt-in | `COMPASS_DECISION_APPLY` default off |
| Eligibility first | Applied IDs ⊆ matcher-eligible roster only |
| Thresholds | Noul ≥ 0.70 and Choice confidence ≥ 0.60 (env-overridable) |
| Pad from matcher | Provider reorders confident head; matcher fills remaining slots |
| Fail closed | Abstain / error / stub / threshold miss → matcher unchanged |
| Trial pairing | `APPLY=1` implies shadow evidence (paired compare) for M43 trial |
| Hermetic CI | stub + apply unset |
| No authority leakage | Never approve plans, promote Skills, merge, or unblock tools |
| Ship default-off | Tag v1.43.0; live holdout is operational (`APPLY=1`), not a code gate |

## Resolved open questions (Captain / First Mate)

| # | Question | Decision | Notes |
|---|---|---|---|
| 1 | Default min Noul? | **0.70** | Env: `COMPASS_DECISION_NOUL_MIN`. Tunable in holdout. |
| 2 | Pad short lists from matcher? | **Yes** | Provider never drops matcher top_n slots; only reorders head. |
| 3 | Require SHADOW with APPLY? | **Yes, trial** | `APPLY=1` implies paired shadow evidence under m43 evidence root. |
| 4 | Holdout missed-load tolerance? | **5% relative** | Primary metric: wrong/unnecessary skill-load rate vs matcher holdout. |
| 5 | Ship default-off or hold tag? | **Ship v1.43.0 default-off** | Same pattern as M39/M41. |

### First Mate notes on the LLM draft

- Domain language is **skills** (`recommended_skill_ids`), not “providers.”
- Env names use `COMPASS_DECISION_NOUL_MIN` / `COMPASS_DECISION_CONF_MIN` (not `APPLY_MIN_*`).
- `applied: true` only when the final ranking **differs** from matcher.
- M41 internal Jev gate (0.30) stays for suggestion generation; M43 apply floors (0.70 / 0.60) are a separate, stricter promotion gate.

## Scope

**In:** apply policy helper + resolve wiring; evidence under
`.agent/evidence/m43-jev-ranking-enablement/`; hermetic tests; holdout gate doc;
docs/ADR-060; VERSION 1.43.0.

**Out:** review triage; agent routing; TI via Jev; CI default-on; unpinning model;
matcher weight file writes; changing matcher algorithm.

## Desired behavior

```
rank_skills() → recommended := matcher top_n
if APPLY or SHADOW (APPLY implies shadow in trial):
    suggest_skills()
    if APPLY and not abstain and gates pass and ⊆ eligible:
        recommended := provider head + matcher pad (top_n)
        applied := (recommended != matcher)
    write evidence (m43 when APPLY path; m41 shadow-only unchanged)
```

Env:

| Variable | Default | Role |
|---|---|---|
| `COMPASS_DECISION_APPLY` | unset/off | Opt-in apply |
| `COMPASS_DECISION_NOUL_MIN` | `0.70` | Apply Noul floor |
| `COMPASS_DECISION_CONF_MIN` | `0.60` | Apply Choice confidence floor |
| `COMPASS_DECISION_SHADOW` | unset | Explicit shadow; also implied by APPLY in M43 trial |
| `COMPASS_DECISION_PROVIDER` | `stub` | unchanged |
| `COMPASS_JEV_*` | M41 contract | unchanged |

## Workstreams

| ID | Work |
|---|---|
| WS1 | `apply.py` policy: env, gates, eligibility filter, matcher pad |
| WS2 | Resolve wiring + evidence `applied` / applied ranking; APPLY⇒shadow |
| WS3 | Hermetic tests (apply / abstain / OOR / failure / default-off / shadow regression / pad) |
| WS4 | Holdout gate doc + evidence scaffold |
| WS5 | Docs ADR-060 + TESTING/PROGRESS/CHANGELOG/VERSION 1.43.0 |
| WS6 | Optional Captain-local live smoke (out of CI) |

## Acceptance criteria

1. Defaults: rankings bit-identical to matcher; doctor/tests/evals green; no network.
2. file + APPLY=1 with high-confidence fixture changes rankings; evidence `applied: true`.
3. Abstain / low Noul / low conf / OOR / stub / errors → matcher unchanged; `applied: false`.
4. Applied IDs ⊆ eligible roster (unit invariant); pad fills from matcher.
5. Shadow-only (no APPLY) still non-mutating.
6. Plans reference evidence path/ID only.
7. Holdout gate doc under `.agent/evidence/m43-jev-ranking-enablement/`.
8. No agent-router / boundary / plan-approval / promotion changes.
9. Rollback: unset APPLY → matcher-only; tag `rollback/pre-m43-jev-ranking-enablement`.

## Evaluation gate (Captain-local)

Holdout labeled set: ≤5% relative regression on wrong/unnecessary skill-load rate
vs matcher; no eligibility bypasses; easy rollback. CI green does not require live Jev.

## Approval boundary

Captain approved 2026-09-24. Product implementation proceeds on this plan.
