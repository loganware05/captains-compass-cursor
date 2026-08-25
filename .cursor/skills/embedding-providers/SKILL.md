---
name: embedding-providers
description: Rebuilds and queries fixture dense embedding indexes with TF-IDF always as fallback
---

# Embedding Providers

## Use this Skill when

The Captain wants **opt-in dense embedding** search for Knowledge Steward while
keeping **TF-IDF as the always-on fallback**. Milestone 11 ships **fixture +
protocol only** — no live embedding HTTP APIs.

## Inputs

- Knowledge items under `.agent/knowledge/items/`
- Env `COMPASS_EMBEDDING_PROVIDER` (`tfidf` default | `fixture`)
- Explicit rebuild CLI

## Procedure

1. Default path stays TF-IDF (`COMPASS_EMBEDDING_PROVIDER` unset or `tfidf`):

   ```bash
   ./scripts/rebuild-knowledge-vector-index.sh
   ./scripts/query-knowledge.sh --query "matcher tuning" --mode hybrid
   ```

2. Opt into fixture dense embeddings (offline hash projection; no network):

   ```bash
   COMPASS_EMBEDDING_PROVIDER=fixture \
     ./scripts/rebuild-knowledge-embedding-index.sh
   COMPASS_EMBEDDING_PROVIDER=fixture \
     ./scripts/query-knowledge.sh --query "matcher tuning" --mode vector
   ```

3. Confirm results include `vector_backend: fixture-embedding` when dense index
   hits; missing dense index falls back to TF-IDF automatically.
4. Never enable live OpenAI-compatible HTTP in CI (deferred past M11).

## Output

- `.agent/knowledge/embedding-index.json` (dense; optional)
- Existing `.agent/knowledge/vector-index.json` (TF-IDF; always rebuildable)

## Prohibited actions

- Network embedding API calls in CI or default path
- Removing or skipping TF-IDF fallback
- Mutating matcher weights from embedding scores
- Auto-rebuild on workstream close
