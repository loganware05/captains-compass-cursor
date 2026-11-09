# WorkOS AuthKit identity / RBAC (I5)

Fixture-first `northstar identity` surface for WorkOS AuthKit-shaped
organization membership + role evidence.

**WorkOS roles never replace GitHub Captain approval.**

## Gates

| Env | Purpose |
|---|---|
| `COMPASS_IDENTITY_ENABLED=1` | Enable CLI (alias `COMPASS_WORKOS_ENABLED=1`) |
| `COMPASS_IDENTITY_LIVE=1` | Live dual-gate (skeleton only; API deferred) |
| `COMPASS_WORKOS_API_KEY` / `WORKOS_API_KEY` | Live token (never committed) |
| `COMPASS_WORKOS_FIXTURES` | Optional fixture path override |

## Commands

```bash
COMPASS_IDENTITY_ENABLED=1 ./scripts/northstar identity sync
COMPASS_IDENTITY_ENABLED=1 ./scripts/northstar identity list
COMPASS_IDENTITY_ENABLED=1 ./scripts/northstar identity show --packet-id ID
```

`northstar workos …` is an alias for the same surface.

## Storage

Packets land under `.agent/identity/workos/` with:

- `grants_captain_approval: false`
- `live_synced: false`
- authority locks const false

## Overseer

Snapshots expose `identity_refs` and `dev-workos-identity` when packets exist.
