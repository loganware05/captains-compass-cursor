> **APPROVED** 2026-09-24. Active root plan mirrors this file. Linear: OVA-56.

# Implementation Plan — M44 / Jev Decision Service (Review Triage Shadow)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m44-jev-review-triage` |
| Approved | 2026-09-24 — Captain: "I've merged PR #181, proceed with the plan" (next Captain-ordered Decision Service trial) |
| Linear | [OVA-56](https://linear.app/ovaltechnologysolutions/issue/OVA-56/m44-jev-decisionprovider-review-triage-shadow-v1440) |
| Supersedes | — (builds on M41/M43 DecisionProvider; new review surface) |
| Product | **NorthStar** |
| Baseline | **v1.43.0** @ `cc1de5c` (post-M43 #181) |
| Prepared | 2026-09-24 |
| Spec source | Notion Decision Service draft §A; ADR-058/060 next-trial notes; Captain order |
| Proposed release | **v1.44.0** (default-off shadow) |
| Rollback | `rollback/pre-m44-jev-review-triage` @ `cc1de5c` |
| Branch | `cursor/m44-jev-review-triage-753c` |
| Captain | Logan Ware |
| Pinned model | **`jev-1.13.0`** |

## Request

Add **shadow-first review triage** via DecisionProvider on the code-review
pipeline: given bounded change metadata, record investigation priority /
specialist-security-warranted signals **without** mutating specialist
composition, findings, boundary, verify, or report authority.

## Problem

M43 enables opt-in skill ranking apply. Review triage was the next ordered
trial. Notion §A asks whether a change warrants specialist security
investigation; attaching that without a shadow gate would risk wrong
escalations or (worse) suppressing required review.

## Decision summary

| Principle | Implication |
|---|---|
| Shadow first | `COMPASS_DECISION_REVIEW_SHADOW` default off; never mutates review outputs |
| Separate flags | Review shadow ≠ skill `COMPASS_DECISION_SHADOW` / `APPLY` |
| Fail closed | Abstain / error / stub → baseline review unchanged |
| Compact state | Paths, domains, path flags; no secrets / whole repos / unfiltered diffs |
| Authority | Specialists + boundary + verify + report remain sole gates |
| Hermetic CI | stub + review shadow unset |
| No apply in M44 | Mutating specialist routing deferred (later Captain-gated plan) |

## Scope

**In:** `triage_review` protocol method; types + question revision; stub/file/jev;
pipeline shadow hook after specialist composition; evidence under
`.agent/evidence/m44-jev-review-triage/`; hermetic tests; docs/ADR-061; VERSION 1.44.0.

**Out:** Applying triage to suppress/reorder emitters; agent routing; tool-call
security triage (Notion §B); TI via Jev; CI default-on; unpinning model;
changing M31 finding outcomes.

## Desired behavior

```
detect → investigate → compose_specialist_candidates
if COMPASS_DECISION_REVIEW_SHADOW and provider ≠ stub:
    triage_review(compact_change_state) → evidence only
boundary → verify → report   # unchanged
```

Env: `COMPASS_DECISION_REVIEW_SHADOW` (default off). Reuses
`COMPASS_DECISION_PROVIDER` / `COMPASS_JEV_*` / fixtures dir.

## Workstreams

| ID | Work |
|---|---|
| WS1 | Types + question revision `review_triage_v1` |
| WS2 | Protocol `triage_review` on stub/file/jev |
| WS3 | Compact change state builder (path flags, no diffs by default) |
| WS4 | Shadow evidence writer + pipeline hook |
| WS5 | Hermetic tests + CI assert flag unset |
| WS6 | Docs ADR-061 + TESTING/PROGRESS/CHANGELOG/VERSION |

## Acceptance criteria

1. Defaults: review pipeline bit-identical; doctor/tests green; no network.
2. file + REVIEW_SHADOW=1 writes evidence under m44 path; findings/candidates unchanged.
3. Abstain / stub / errors → no mutation; evidence may record abstain.
4. Compact state refuses secrets / unbounded diffs.
5. Plans/reports reference evidence path/ID only when present.
6. No specialist / boundary / verify / merge / tool-allowlist authority changes.
7. Rollback: unset `COMPASS_DECISION_REVIEW_SHADOW`.

## Approval boundary

Captain directed continuation of the Decision Service sequence after M43 merge.
Product implementation proceeds on this shadow-first plan.
