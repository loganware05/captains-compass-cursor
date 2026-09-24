> Draft awaiting Captain approval. Active root plan is the same content while this branch is open.

# Implementation Plan — M43 / Jev Decision Service (Ranking Enablement)

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `m43-jev-ranking-enablement` |
| Approved | — |
| Supersedes | — (builds on M41 ADR-058 shadow-only DecisionProvider) |
| Product | **NorthStar** |
| Baseline | **v1.42.0** @ `ed20499` (rebaseline to post-M42 `main` at approval if #180 merges first) |
| Prepared | 2026-09-24 |
| Spec source | ADR-058; `docs/integrations/decision-provider.md`; Captain order after M41: ranking enablement → review triage → agent routing |
| Proposed release | **v1.43.0** (tentative) |
| Rollback | Tag `rollback/pre-m43-jev-ranking-enablement` at approval-time `main` |
| Branch | `cursor/m43-jev-ranking-enablement-753c` (plan draft) |
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
| Thresholds | Below Noul/confidence floor → keep matcher |
| Fail closed | Abstain / error / stub → matcher |
| Shadow OK | Shadow may coexist; `applied: true` only when rankings change |
| Hermetic CI | stub + apply off |
| No authority leakage | Never approve plans, promote Skills, merge, or unblock tools |

## Scope

**In:** apply helper + resolve wiring; evidence under `.agent/evidence/m43-jev-ranking-enablement/` (path/ID refs in plans); hermetic tests; holdout eval gate; docs/ADR.

**Out:** review triage; agent routing; TI via Jev; CI default-on; unpinning model; matcher weight file writes.

## Desired behavior

```
rank_skills() → optional suggest_skills()
if APPLY and not abstain and ⊆ eligible and thresholds pass:
    recommended_skill_ids := provider order (eligible only); evidence.applied=true
else:
    matcher rankings; applied=false
```

Env: `COMPASS_DECISION_APPLY` (default off); `COMPASS_DECISION_APPLY_MIN_NOUL` (default TBD).

## Workstreams

| ID | Work |
|---|---|
| WS1 | Apply policy helper + env + eligibility filter |
| WS2 | Resolve wiring + evidence `applied` flag |
| WS3 | Hermetic tests (apply / abstain / OOR / failure / default-off / shadow regression) |
| WS4 | Holdout eval report vs matcher |
| WS5 | Docs ADR-060 + TESTING/PROGRESS/CHANGELOG |
| WS6 | Optional Captain-local live smoke |

## Acceptance criteria

1. Defaults: rankings bit-identical to matcher; doctor/tests/evals green; no network.
2. file + APPLY=1 with high-confidence fixture changes rankings; evidence `applied: true`.
3. Abstain / low Noul / OOR / stub / errors → matcher unchanged.
4. Applied IDs ⊆ eligible roster (unit invariant).
5. Shadow-only still non-mutating.
6. Plans reference evidence path/ID only.
7. Holdout report under `.agent/evidence/m43-jev-ranking-enablement/`.
8. No agent-router / boundary / plan-approval / promotion changes.
9. Rollback: unset APPLY → matcher-only.

## Evaluation gate (Captain-local live apply)

Holdout labeled set: improve wrong/unnecessary loads vs matcher; no eligibility bypasses; easy rollback. CI green does not require live Jev.

## Open questions

1. Default min Noul for first enablement?
2. Pad short provider lists from matcher (proposed yes)?
3. Require SHADOW=1 with APPLY during trial?
4. Max allowed missed-load regression on holdout?
5. Ship v1.43.0 default-off before holdout live gate, or hold tag?

## Approval boundary

**No product implementation until Captain explicitly approves this plan.**

## First Mate recommendation

Approve opt-in thresholded apply default-off; keep review triage and agent routing as later plans. Answer open questions in the approval utterance when possible.
