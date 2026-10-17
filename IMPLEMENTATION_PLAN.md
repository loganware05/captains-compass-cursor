# Implementation Plan — C2 Cognitive Core Memory and Retrieval

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `c2-cognitive-core-memory-retrieval` |
| Issue | [#203](https://github.com/loganware05/captains-compass-cursor/issues/203) |
| Notion | [Cognitive Core — C2](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.60.1** @ `2314def` |
| Branch | `cursor/203-c2-memory-retrieval-64df` |
| Rollback | `rollback/pre-c2-cognitive-core-memory-retrieval` @ `2314def` |
| Release | **v1.61.0** |
| Captain | Logan Ware |
| Created | 2026-10-16 |
| Approved | 2026-10-17 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-17 |
| Notes | Chat continuation from prior IDE agents session (“M51 Kimi K3 project overseer”); explicit “approve the c2 plan”. Standing order: implement → validate → commit → open PR. Issue #203 already referenced this Plan ID at AWAITING APPROVAL; repo plan was missing and is reconstituted here from #203 + Notion C2 + C1 surfaces. |

## Request

Ship Cognitive Core **C2 — Memory and Retrieval**: gated hybrid retrieval over C1 project-state + Knowledge Steward, with Decision/ADR citation links and a hermetic gold-set harness (target ≥90% evidence-linked answers on a 30-question held-out set).

## Problem Statement

C1 (`northstar brain sync|status|show`) persists SHA-cited project-state but does not answer task queries with evidence-linked memory. Knowledge Steward hybrid search exists separately (`query-knowledge.sh`) and is not composed with brain freshness, snapshot citations, or ADR decision links. Operators need one gated context surface before C3–C7 Adaptive Intelligence work.

## Desired Outcome

```bash
COMPASS_BRAIN_ENABLED=1 \
./scripts/northstar brain context --query "…" [--mode hybrid|keyword|vector] [--top N] --repo .
```

Returns JSON with project-state freshness/SHA, ranked knowledge hits, decision/ADR links, and citation refs. Always `approved_for_execution: false` / `authority_mutation: false`. Hermetic gold-set reports ≥90% evidence-linked.

## Acceptance Criteria

- [x] `northstar brain context --query` behind `COMPASS_BRAIN_ENABLED` (fail-closed when unset)
- [x] Context composes latest C1 project-state (freshness + SHA) with Knowledge Steward hybrid/keyword/vector search
- [x] Decision/ADR links from `DECISIONS.md` (and/or knowledge `kind=decision`) cited in the response
- [x] Schema-validated response (`brain-context-response`) locking authority flags false
- [x] Hermetic 30-question gold-set harness; ≥90% evidence-linked on fixture
- [x] Doctor recognizes new schema; unit tests green
- [x] Memory docs + CHANGELOG + VERSION **v1.61.0**; ADR-079
- [x] Evidence under `.agent/evidence/c2-cognitive-core-memory-retrieval/`
- [ ] PR opened (standing order)

## Non-Goals

- C3 Difficulty / capability fit
- C4 Adaptive Development Loop
- C5 Adaptive routing / model switching
- C6 REA deep analysis
- C7 Training bridge / weight export
- Live embedding/API required for CI (keyword fallback sufficient)
- Auto-rewrite of canonical memory docs
- External cognitive-core package extract

## Affected systems

| Area | Change |
|---|---|
| `orchestrator/cognitive/` | `context.py`, decision-link helper; `service.py` |
| `orchestrator/schemas/` | `brain-context-response.schema.json` |
| `scripts/run-brain.sh`, `scripts/northstar` | `context` subcommand |
| `scripts/doctor.sh` | schema presence check |
| `tests/orchestrator/` + fixtures | C2 unit + gold-set |
| Project memory | PLAN / PROGRESS / CHANGELOG / DECISIONS / TESTING / VERSION / README |

## Workstreams (sequential)

1. **Schema + retrieval compose** — context builder, decision links, service API
2. **CLI + launcher** — `brain context` wiring
3. **Gold-set harness** — 30 hermetic questions + score report
4. **Docs / evidence / release bump**

## Validation

- Static: `./scripts/doctor.sh`
- Unit: `test_c2_cognitive_core_memory_retrieval.py` (+ C1 still green)
- Gold-set: hermetic ≥90% evidence-linked
- Security: no secrets in context payload; authority flags const false
- Rollback review: tag `rollback/pre-c2-cognitive-core-memory-retrieval`

## Autonomy Budget

| Limit | Value |
|---|---|
| Maximum iterations | 8 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 240 |
| Maximum estimated cost (USD) | 0 (no paid GPU) |
| Stop on scope change | true |
| Stop on destructive operation | true |

## Rollback

```bash
git checkout main
git reset --hard rollback/pre-c2-cognitive-core-memory-retrieval
# or revert the merge commit of the C2 PR
```

## Definition of Done

Acceptance criteria checked; evidence recorded; PR open; First Mate inspected.
