# Security review — c2-cognitive-core-memory-retrieval

| Item | Assessment |
|---|---|
| Authority expansion | None — schema locks `approved_for_execution` / `authority_mutation` to false |
| Secrets | No new secret surfaces; reuses knowledge secret-path rejection; does not print env |
| Injection | Query is tokenized locally; no shell interpolation of query into subprocess args beyond argv |
| Network | No network required; hybrid falls back to keyword when vector backends absent |
| Persistence | C2 context is ephemeral JSON stdout; does not rewrite canonical memory |
| Gate | Fail-closed without `COMPASS_BRAIN_ENABLED=1` |

Residual risk: low. Operators may see ADR summaries from `DECISIONS.md` (already public in-repo).
