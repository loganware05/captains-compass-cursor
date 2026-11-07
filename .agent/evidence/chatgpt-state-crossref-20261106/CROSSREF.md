# ChatGPT Repository-State Cross-Reference

- **Date:** 2026-11-06
- **Source export:** Obsidian AI Exporter → `repository-state-description-6ad7acfd.md`
  (ChatGPT thread `6ad7acfd…`, messages through integration roadmap I1–I6)
- **Authority checked:** GitHub `origin/main` @ `c46c161` (**VERSION 1.76.0**)
- **Local checkout at inspection:** `main` @ `2314def` (**v1.60.1**, **99 commits behind**)

## Verdict

ChatGPT’s late-thread assessment of NorthStar **matches `origin/main`**. The
local Cursor/T3 working tree is **stale** and still shows the obsolete C2 plan.
Do not implement from the local tree until it is fast-forwarded to `origin/main`.

## Cognitive Core (C1–C7)

| Step (ChatGPT) | Claimed | Repo evidence (`origin/main`) | Status |
|---|---|---|---|
| C1 Source of Truth | v1.60.0 / #200 | `orchestrator/cognitive/`, brain CLI | **Implemented** |
| C2 Memory & Retrieval | v1.61.0 / #204 | cognitive + knowledge hybrid wiring | **Implemented** |
| C3 Difficulty assessment | v1.62.x | `orchestrator/assess/` | **Implemented** |
| C4 Adaptive cycles | v1.63.x | `orchestrator/cycle/` | **Implemented** |
| C5 Model routing | v1.64.x | `orchestrator/route/`, `routing/` | **Implemented** |
| C6 REA | v1.65.x | `orchestrator/rea/` | **Implemented** |
| C7 Training bridge | v1.66.0 / #219 | `orchestrator/train_bridge/` + schemas | **Implemented** |

## Consolidation (N1–N5) — ChatGPT “best next steps”

| Step | ChatGPT recommendation | Repo evidence | Status |
|---|---|---|---|
| N1 Operational Reconciliation | Closeout ledger + `status closeout` | v1.71.1 / #238, `docs/plans/N1_*` | **Done** |
| N2 Product Integration | Real product install proof | v1.72.0 / #239 (sandbox, not bitcoin-data-collector) | **Done** (sandbox target) |
| N3 Adaptive scorecard | Connect learning/routing evals | v1.73.0 / #240, `orchestrator/adaptive/` | **Done**; Level 3 **defer** |
| N3 post-merge closeout | Reconcile docs after #240 | later closeouts through #246 | **Done** |
| N4 Real-world / cross-stack benchmark | Measure baseline vs evidence-informed | v1.75.0 / #243, `orchestrator/benchmark/` | **Done** (hermetic harness; not multi-product live PoV) |
| N5 Experience→intelligence feedback | Skill-fit / routing feedback | v1.76.0 / #244, `orchestrator/feedback/` | **Done** (apply still Captain-gated) |
| Open UI Control Plane | (later ChatGPT note) | v1.74.0–1.74.1 / #241–#242 | **Done** |
| Specialized Model Level 3 | Conditional / defer | PROGRESS + idle plan | **Still deferred** |

## Specialized Model Levels 0–2

| Level | Status on `origin/main` |
|---|---|
| Level 0 held-out eval | Present (`docs/plans/SPECIALIZED_MODEL_LEVEL_0.md`, fixtures) |
| Level 1 LoRA harness | Present |
| Level 2 QLoRA / GPU harness | Present |
| Level 3 larger GPU | **Deferred** (issue #237 historically; no active plan) |
| Live trained production adapter | **Not proven** (harness ≠ trained model) |

## ChatGPT Priority 1–4 (early Oct 20 message)

| Priority | Recommendation | Status vs `origin/main` |
|---|---|---|
| 1 | C7 closeout + memory reconciliation | Superseded by N1; **done** |
| 2 | C1–C7 E2E integration eval | Covered by N2/N3/N4 track; **done** (bounded) |
| 3 | Persistent post-merge oversight | N1 closeout + Overseer surfaces; **done** |
| 4 | Specialized Model experimentation | Harness Levels 0–2 **exist**; PoV still **open** |

## Integration roadmap (final ChatGPT message) — NOT implemented

| ID | Tool | Proposed role | In repo today? |
|---|---|---|---|
| I1 | Sentry | Production incident → evidence | **No** Sentry adapter |
| I2 | T3 Code | Multi-agent execution adapter | **No** T3 execution adapter (operator may use T3; NorthStar has Cursor adapter only) |
| I3 | Apify MCP | External research / TI | **No** Apify provider |
| I4 | Scrimba Explain | `northstar explain` | **No** explain surface |
| I5 | WorkOS | Hosted identity / RBAC | **No** |
| I6 | Cross-provider validation | N4/N5 measure integrations | Blocked on I1–I5 |

## Conversation → NorthStar training gap (Captain request)

Existing pieces that are **adjacent but insufficient**:

- External knowledge ingest: Notion / NotebookLM markdown only
- Behavior exemplars + provenance (M53) from **executions**, not ChatGPT threads
- C7 train bridge trajectories from **experiences/cycles**, not chat exports
- Experience→Skill draft training (product Experiences)

**Missing:** Obsidian AI Exporter / ChatGPT markdown → structured
`(user_prompt, model/source, suggestion, rationale)` records that can feed
Knowledge Steward and (optionally) curated training/exemplar drafts without
auto-authority.

## Recommended Captain next moves

1. Fast-forward local `main` to `origin/main` (v1.76.0) before any implement.
2. Approve a bounded plan for **conversation trajectory ingest** (this session’s proposed plan) **or** choose an integration track (I1 Sentry / I2 T3).
3. Keep Specialized Model Level 3 deferred until Level 0–2 PoV with authorized data.
