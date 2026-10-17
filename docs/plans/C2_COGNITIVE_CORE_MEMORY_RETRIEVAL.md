> **COMPLETE** (2026-10-17) — Merged [#204](https://github.com/loganware05/captains-compass-cursor/pull/204)
> → `main` @ `f1ae35d` (**v1.61.0**). Plan ID `c2-cognitive-core-memory-retrieval`.
> Issue: [#203](https://github.com/loganware05/captains-compass-cursor/issues/203) (closed).
> Rollback: `rollback/pre-c2-cognitive-core-memory-retrieval` @ `2314def`.
> Evidence: `.agent/evidence/c2-cognitive-core-memory-retrieval/`.

# C2 — Cognitive Core Memory and Retrieval

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (C2 section)

Prerequisite: C1 shipped (v1.60.0 / closeout v1.60.1); Knowledge Steward hybrid search (M5/M6).

## One-line summary

Gated `northstar brain context` composing C1 project-state + hybrid knowledge search with ADR decision links and a hermetic gold-set (≥90% evidence-linked).

## Shipped operator surface

```bash
COMPASS_BRAIN_ENABLED=1 \
./scripts/northstar brain context --query "…" [--mode hybrid|keyword|vector] [--top N] --repo .
```

## Non-goals (honored)

C3–C7; live embeddings required for CI; memory auto-rewrite.
