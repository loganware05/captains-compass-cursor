> **APPROVED** 2026-09-25. Active root plan mirrors this file. Linear: OVA-57.

# Implementation Plan — M45 / Jev Decision Service (Agent Routing Shadow)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m45-jev-agent-routing` |
| Approved | 2026-09-25 — Captain: "I've merged PR #182, proceed with agent routing" |
| Linear | [OVA-57](https://linear.app/ovaltechnologysolutions/issue/OVA-57/m45-jev-decisionprovider-agent-routing-shadow-v1450) |
| Supersedes | — (builds on M41–M44 DecisionProvider; new agent-routing surface) |
| Product | **NorthStar** |
| Baseline | **v1.44.0** @ `0d7d78d` (post-M44 #182) |
| Prepared | 2026-09-25 |
| Spec source | Notion Decision Service draft (agent routing row); ADR-058–061; agent-routing-contract.md |
| Proposed release | **v1.45.0** (default-off shadow) |
| Rollback | `rollback/pre-m45-jev-agent-routing` @ `0d7d78d` |
| Branch | `cursor/m45-jev-agent-routing-753c` |
| Captain | Logan Ware |
| Pinned model | **`jev-1.13.0`** |

## Request

Add **shadow-first agent routing** via DecisionProvider: semantic task-fit signal
over **already hard-filtered** eligible agents — without mutating selection,
`dispatch_ready`, wakeability, allowlist, budget, or hard filters.

## Problem

Captain-ordered Decision Service sequence ends with agent routing. Notion
assigns Jev a semantic fit signal only; hard filters remain sole eligibility /
dispatch authority. Shipping apply-first would risk reordering past wakeability
or allowlist gates.

## Decision summary

| Principle | Implication |
|---|---|
| Shadow first | `COMPASS_DECISION_AGENT_ROUTING_SHADOW` default off; never mutates selection |
| Eligible only | Provider roster ⊆ `eligible_agent_ids` after hard filters |
| Fail closed | Abstain / error / stub → baseline routing unchanged |
| Separate flags | Independent of skill SHADOW/APPLY and REVIEW_SHADOW |
| Compact state | Objective + eligible agent summaries; no secrets / full memory |
| Authority | Wakeability, allowlist, budget, hard filters, final dispatch stay sole |
| Hermetic CI | stub + agent-routing shadow unset |
| No apply in M45 | Mutating selection deferred to a later Captain-gated plan |

## Scope

**In:** `suggest_agents` protocol method; types + `agent_routing_v1`; stub/file/jev;
shadow evidence under `.agent/evidence/m45-jev-agent-routing/`; CLI path/ID refs;
hermetic tests; docs/ADR-062; VERSION 1.45.0.

**Out:** Mutating `selected_agent_id` / scores / `dispatch_ready`; re-admitting
filtered agents; tool-call security triage; TI via Jev; CI default-on; unpinning.

## Desired behavior

```
route_agents() → hard filters → eligible set → weighted selection
if COMPASS_DECISION_AGENT_ROUTING_SHADOW and provider ≠ stub:
    suggest_agents(objective + eligible profiles only) → evidence
selected_agent_id / dispatch_ready UNCHANGED
```

## Workstreams

| ID | Work |
|---|---|
| WS1 | Types + question revision `agent_routing_v1` |
| WS2 | Protocol `suggest_agents` on stub/file/jev |
| WS3 | Shadow writer + attach helper (eligible-only roster) |
| WS4 | CLI `score-agent-routing.sh` path/ID refs |
| WS5 | Hermetic tests + CI assert flag unset |
| WS6 | Docs ADR-062 + TESTING/PROGRESS/CHANGELOG/VERSION |

## Acceptance criteria

1. Defaults: routing bit-identical; doctor/tests green; no network.
2. file + AGENT_ROUTING_SHADOW=1 writes m45 evidence; selection unchanged.
3. Provider never receives filtered-out agent IDs.
4. Abstain / stub / errors → no mutation.
5. Plans/CLI store path/ID refs only when present.
6. No hard-filter / wakeability / budget / dispatch authority changes.
7. Rollback: unset `COMPASS_DECISION_AGENT_ROUTING_SHADOW`.

## Approval boundary

Captain directed agent routing after M44 merge. Product implementation proceeds
on this shadow-first plan.
