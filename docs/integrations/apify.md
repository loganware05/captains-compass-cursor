# Apify research / Technology Intelligence (I3)

Fixture-first Apify Actor discovery into NorthStar TI candidates and optional
research packets. **Never auto-runs Actors** in v1.80.0 (`called_actor: false`).

## TI provider

```bash
COMPASS_TI_PROVIDER=apify-file ./scripts/capability-plan.sh "web research"
```

Fixtures: `orchestrator/providers/technology_intelligence/fixtures/apify/`.
Override with `COMPASS_APIFY_TI_FIXTURES_DIR`.

Live aliases (`apify`, `apify-live`, `apify-mcp`) require dual gates and still
fail closed (MCP skeleton; call-actor deferred).

## CLI

```bash
COMPASS_APIFY_ENABLED=1 ./scripts/northstar apify search --query "web research"
COMPASS_APIFY_ENABLED=1 ./scripts/northstar apify list
COMPASS_APIFY_ENABLED=1 ./scripts/northstar apify show --packet-id ID
```

Packets land under `.agent/research/apify/` with authority locks const false.

## Gates

| Env | Purpose |
|---|---|
| `COMPASS_APIFY_ENABLED=1` | Enable CLI surface |
| `COMPASS_APIFY_LIVE=1` | Live dual-gate (skeleton only) |
| `COMPASS_APIFY_TOKEN` / `APIFY_TOKEN` | Live token (never committed) |

## Overseer

Snapshots expose `research_refs` and `dev-apify-research` when packets exist.
