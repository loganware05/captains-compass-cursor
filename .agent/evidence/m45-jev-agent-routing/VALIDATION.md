# M45 Validation — Agent Routing Shadow

## Hermetic

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -B -m unittest \
  tests.orchestrator.test_m41_decision_provider \
  tests.orchestrator.test_m45_agent_routing_shadow -v
```

Defaults: `COMPASS_DECISION_AGENT_ROUTING_SHADOW` unset → routing unchanged; no network.

## File-provider shadow smoke

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_AGENT_ROUTING_SHADOW=1 \
./scripts/score-agent-routing.sh \
  --registry path/to/agents.json \
  --objective path/to/objective.json
```

Expect `decision_agent_routing` path/ID refs and evidence under
`.agent/evidence/m45-jev-agent-routing/shadow/` with `applied: false`.
`selected_agent_id` / `dispatch_ready` match baseline.

## Rollback

Unset `COMPASS_DECISION_AGENT_ROUTING_SHADOW`. Tag: `rollback/pre-m45-jev-agent-routing`.
