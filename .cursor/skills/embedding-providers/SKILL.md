---
name: embedding-providers
description: Rebuilds and queries fixture or OpenAI-compatible dense embedding indexes with TF-IDF always as fallback
---

# Embedding Providers

## Use this Skill when

The Captain wants **opt-in dense embedding** search for Knowledge Steward while
keeping **TF-IDF as the always-on fallback**.

## Inputs

- Knowledge items under `.agent/knowledge/items/`
- Env `COMPASS_EMBEDDING_PROVIDER` (`tfidf` default | `fixture` | `openai-compatible`)
- For live HTTP: `COMPASS_EMBEDDING_API_KEY` (required), optional
  `COMPASS_EMBEDDING_BASE_URL`, `COMPASS_EMBEDDING_MODEL`,
  `COMPASS_EMBEDDING_DIMENSIONS`
- Explicit rebuild CLI

## Procedure

1. Default path stays TF-IDF (`COMPASS_EMBEDDING_PROVIDER` unset or `tfidf`):

   ```bash
   ./scripts/rebuild-knowledge-vector-index.sh
   ./scripts/query-knowledge.sh --query "matcher tuning" --mode hybrid
   ```

2. Opt into fixture dense embeddings (offline; no network):

   ```bash
   COMPASS_EMBEDDING_PROVIDER=fixture \
     ./scripts/rebuild-knowledge-embedding-index.sh
   COMPASS_EMBEDDING_PROVIDER=fixture \
     ./scripts/query-knowledge.sh --query "matcher tuning" --mode vector
   ```

3. Opt into **OpenAI-compatible** embeddings (Captain local only; never CI):

   ```bash
   export COMPASS_EMBEDDING_PROVIDER=openai-compatible
   export COMPASS_EMBEDDING_API_KEY=...   # never commit
   # optional:
   # export COMPASS_EMBEDDING_BASE_URL=https://api.openai.com/v1
   # export COMPASS_EMBEDDING_MODEL=text-embedding-3-small
   ./scripts/rebuild-knowledge-embedding-index.sh
   ./scripts/query-knowledge.sh --query "matcher tuning" --mode vector
   ```

4. Missing dense index or live HTTP failure → automatic **TF-IDF fallback**.
5. Never enable live embedding HTTP in CI.

## Output

- `.agent/knowledge/embedding-index.json` (dense; optional)
- Existing `.agent/knowledge/vector-index.json` (TF-IDF; always rebuildable)

## Prohibited actions

- Network embedding API calls in CI or default path
- Committing API keys or logging Authorization headers
- Removing or skipping TF-IDF fallback
- Mutating matcher weights from embedding scores
- Auto-rebuild on workstream close
