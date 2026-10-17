> **APPROVED** (2026-10-17) — Plan ID `c2-cognitive-core-memory-retrieval`.
> Issue: [#203](https://github.com/loganware05/captains-compass-cursor/issues/203).
> PR: [#204](https://github.com/loganware05/captains-compass-cursor/pull/204).
> Branch: `cursor/203-c2-memory-retrieval-64df` · Rollback `rollback/pre-c2-cognitive-core-memory-retrieval`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C2 — Cognitive Core Memory and Retrieval

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (C2 section)

Prerequisite: C1 shipped (v1.60.0 / closeout v1.60.1); Knowledge Steward hybrid search (M5/M6).

## One-line summary

Gated `northstar brain context` composing C1 project-state + hybrid knowledge search with ADR decision links and a hermetic gold-set (≥90% evidence-linked).

## Baseline

v1.60.1 @ `2314def` → proposed release **v1.61.0**

## Proposed operator surface

```bash
COMPASS_BRAIN_ENABLED=1 \
./scripts/northstar brain context --query "…" [--mode hybrid|keyword|vector] [--top N] --repo .
```

## Non-goals

C3–C7 (difficulty, cycle, routing, REA, training); live embeddings required for CI; memory auto-rewrite.

## Linear / GitHub

| Item | Link |
|---|---|
| Issue | [#203](https://github.com/loganware05/captains-compass-cursor/issues/203) |
| Notion | [Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
