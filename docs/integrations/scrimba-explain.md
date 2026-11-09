# Scrimba Explain (I4)

Fixture-first `northstar explain` surface for Scrimba-style explainer packets.
**Distinct from** Overseer `northstar status explain`.

Never auto-publishes (`auto_published: false`) and does not stream live MCP in
v1.81.0 (`streamed_live: false`).

## Gates

| Env | Purpose |
|---|---|
| `COMPASS_EXPLAIN_ENABLED=1` | Enable CLI |
| `COMPASS_EXPLAIN_LIVE=1` | Live dual-gate (skeleton only; streaming deferred) |

## Commands

```bash
COMPASS_EXPLAIN_ENABLED=1 \
  ./scripts/northstar explain create --topic "How approval gates work"

COMPASS_EXPLAIN_ENABLED=1 ./scripts/northstar explain list
COMPASS_EXPLAIN_ENABLED=1 ./scripts/northstar explain show --packet-id ID
```

Optional `--mcp pr` records the PR MCP endpoint
(`https://scrimba.com/explain/pr/mcp`) on the fixture packet; default records
`https://scrimba.com/explain/mcp`.

## Storage

Packets land under `.agent/explainers/`. Project Overseer snapshots surface
them as `explainer_refs` (`claim_kind: external`).

## Live MCP (deferred)

Real streaming via Scrimba MCP tools
(`start_explainer_stream` / `append_explainer_chunk` / `finish_explainer_stream`)
is out of scope for v1.81.0. Captain claims Scrimba drafts manually.
