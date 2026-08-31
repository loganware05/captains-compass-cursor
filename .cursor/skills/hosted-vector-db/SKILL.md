---
name: hosted-vector-db
description: Syncs and queries hosted pgvector/Neon knowledge vectors with namespace isolation and TF-IDF fallback
---

# Hosted Vector DB (pgvector / Neon)

## Use this Skill when

The Captain wants **hosted semantic search** for Knowledge Steward beyond
file-backed TF-IDF and local dense indexes, using a shared Neon/pgvector index
with **per-repo namespaces**.

## Cost note (M13 decision)

Neon/pgvector was chosen over Pinecone for Compass scale: both are **$0 on free
tiers** today, but Pinecone Standard carries a **$50/month minimum** once Starter
limits are exceeded; Neon Launch is pay-as-you-go with no monthly floor.

## Inputs

- Approved IMPLEMENTATION_PLAN milestone (M13+)
- Env `COMPASS_VECTOR_PROVIDER=pgvector` (live) or `mock` (tests)
- Env `COMPASS_VECTOR_DATABASE_URL` (Neon Postgres DSN; never commit)
- Env `COMPASS_VECTOR_NAMESPACE` (recommended; default is repo directory name)
- Embedding provider: `COMPASS_EMBEDDING_PROVIDER=fixture` or `openai-compatible`
- Optional: `pip install 'psycopg[binary]'` for live Neon sync/query

## Procedure

1. Default path stays file-backed (`COMPASS_VECTOR_PROVIDER=file` or unset):

   ```bash
   ./scripts/rebuild-knowledge-vector-index.sh
   ./scripts/query-knowledge.sh --query "approval gate" --mode hybrid
   ```

2. Bootstrap pgvector schema on Neon (Captain local):

   ```bash
   export COMPASS_VECTOR_DATABASE_URL='postgresql://...'
   export COMPASS_VECTOR_DIMENSIONS=32   # match embedding provider
   ./scripts/init-pgvector-schema.sh --apply
   ```

3. Sync knowledge embeddings to hosted store (explicit CLI):

   ```bash
   export COMPASS_VECTOR_PROVIDER=pgvector
   export COMPASS_VECTOR_NAMESPACE=captains-compass-cursor
   export COMPASS_EMBEDDING_PROVIDER=fixture   # or openai-compatible + API key
   ./scripts/sync-knowledge-vector-db.sh
   ```

4. Query hosted vectors:

   ```bash
   COMPASS_VECTOR_PROVIDER=pgvector \
   COMPASS_VECTOR_DATABASE_URL='postgresql://...' \
   COMPASS_VECTOR_NAMESPACE=captains-compass-cursor \
   COMPASS_EMBEDDING_PROVIDER=fixture \
     ./scripts/query-knowledge.sh --query "matcher tuning" --mode vector
   ```

5. On missing hosted backend, live embed failure, or empty hosted index → **TF-IDF
   fallback** (same as M11/M12).

## Output

- Rows in `compass_knowledge_vectors` keyed by `(namespace, item_id)`
- Query results tagged `vector_backend: pgvector` (or `pgvector-mock` in tests)

## Prohibited actions

- Live Neon/pgvector in CI or default hooks
- Committing database URLs or API keys
- Auto-sync on workstream close
- Removing TF-IDF fallback
