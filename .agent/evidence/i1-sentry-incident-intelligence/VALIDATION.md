# Validation — i1-sentry-incident-intelligence (#249)

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_i1_sentry*.py' -v
./scripts/doctor.sh
COMPASS_SENTRY_INGEST_ENABLED=1 ./scripts/northstar sentry fetch
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status explain --repo .
```

## Overseer note

Snapshots must include `incident_refs` / `conversation_refs` and
`dev-active-plan` findings when an APPROVED plan is present. Canonical memory
is never auto-rewritten.
