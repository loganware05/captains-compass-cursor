# Sentry incident intelligence (I1)

Gated **read-only** Sentry issue ingest into NorthStar evidence packets.
Never writes to Sentry and never grants repair authority.

## Gates

```bash
COMPASS_SENTRY_INGEST_ENABLED=1          # required
COMPASS_SENTRY_LIVE=1                    # optional live API
COMPASS_SENTRY_AUTH_TOKEN=…              # or SENTRY_AUTH_TOKEN
COMPASS_SENTRY_ORG=…                     # live org slug
COMPASS_SENTRY_PROJECT=…                 # live project slug
```

Default mode is **fixture** (CI-safe). Live requires https-only API access.

## Commands

```bash
COMPASS_SENTRY_INGEST_ENABLED=1 \
  ./scripts/northstar sentry fetch [--fixture PATH]

COMPASS_SENTRY_INGEST_ENABLED=1 COMPASS_SENTRY_LIVE=1 \
  ./scripts/northstar sentry fetch --org ORG --project PROJECT [--issue-id ID]

COMPASS_SENTRY_INGEST_ENABLED=1 ./scripts/northstar sentry list
COMPASS_SENTRY_INGEST_ENABLED=1 ./scripts/northstar sentry show --packet-id ID
```

## Storage

Packets land under `.agent/incidents/sentry/`. Project Overseer snapshots
surface them as `incident_refs` (claim_kind: external) on system-map.

## Overseer

```bash
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
```

Snapshots include active-plan development findings plus incident/conversation
refs without mutating canonical memory.
