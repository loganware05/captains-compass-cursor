# Validation — conversation-trajectory-ingest (#247)

## Commands

```bash
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_conversation_trajectory_ingest -v
./scripts/doctor.sh
COMPASS_CONVERSATION_INGEST_ENABLED=1 \
  ./scripts/northstar conversation ingest \
  --path tests/fixtures/conversations/obsidian-chatgpt-sample.md
```

## Authority

- Trajectories and knowledge items keep `approved_for_execution=false`,
  `authority_mutation=false`, `auto_promoted=false`.
- Gate fail-closed without `COMPASS_CONVERSATION_INGEST_ENABLED=1`.

## Queued follow-ons

- I1 Sentry — `docs/plans/I1_SENTRY_INCIDENT_INTELLIGENCE.md`
- I2 T3 — `docs/plans/I2_T3_EXECUTION_ADAPTER.md`
