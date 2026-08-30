# Hosted vector DB (pgvector / Neon)

Use with Skills `hosted-vector-db` and `embedding-providers`.

## Provider selection

| Env | Behavior |
|---|---|
| unset / `file` | File TF-IDF + optional local dense index (default) |
| `mock` | In-memory pgvector simulation (CI/tests) |
| `pgvector` | Live Neon/Postgres via `COMPASS_VECTOR_DATABASE_URL` |

## Namespace strategy

Single shared pgvector index; isolate repos with `COMPASS_VECTOR_NAMESPACE`
(Captain-approved: **index with namespaces**).

## Captain-local setup

1. Create a Neon project with the `vector` extension enabled.
2. Run `./scripts/init-pgvector-schema.sh --apply` with `COMPASS_VECTOR_DATABASE_URL`.
3. Install optional driver: `pip install 'psycopg[binary]'`.
4. Set embedding provider + sync via `./scripts/sync-knowledge-vector-db.sh`.

## CI boundary

CI uses `COMPASS_VECTOR_PROVIDER=file` (default). Never point CI at live Neon.

## Rollback

- Set `COMPASS_VECTOR_PROVIDER=file`.
- Optional: `DELETE FROM compass_knowledge_vectors WHERE namespace = '<repo>';`

See ADR-029 in `DECISIONS.md`.
