# T3 Code ExecutionAdapter (I2)

Gated NorthStar-owned execution surface for T3 Code threads. Fixture-first;
optional live HTTPS JSON transport behind a second gate. Never bypasses plan
approval gates.

## Gates

```bash
COMPASS_T3_EXEC_ENABLED=1     # required
COMPASS_T3_EXEC_LIVE=1        # optional; live HTTPS path (default off)
COMPASS_T3_API_BASE=https://… # required for live (https only)
COMPASS_T3_AUTH_TOKEN=…       # required for live Bearer auth
```

## Commands

```bash
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 capabilities

COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 start \
  --plan-id t3-mcp-live-adapter \
  --objective "bounded task" \
  [--allow-fixture-plan]   # hermetic tests only

COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 status --execution-id ID
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 collect --execution-id ID
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 cancel --execution-id ID
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 list
```

`start` requires `IMPLEMENTATION_PLAN.md` Plan ID match and status in
APPROVED / IN PROGRESS / VALIDATING, unless `--allow-fixture-plan`.

## Live HTTPS allowlist

When `COMPASS_T3_EXEC_LIVE=1`, the live adapter calls a NorthStar-owned HTTPS
JSON contract (maps to T3 MCP tools). CI injects `RecordingTransport` — unit
tests never open a network socket.

| Op | Method | Path | T3 MCP tool |
|---|---|---|---|
| capabilities | GET | `/v1/capabilities` | `orchestrator_capabilities` |
| start | POST | `/v1/threads` | `t3_thread_launch` |
| status / collect | GET | `/v1/threads/{id}?view=activity\|messages` | `t3_thread_read` |
| cancel | POST | `/v1/threads/{id}/interrupt` | `t3_thread_interrupt` |

Allowlisted ops only. No auto-merge, no authority mutation, no plan-gate bypass.

## Storage

Runs under `.agent/executions/t3/`. Overseer snapshots expose `execution_refs`.

## Authority

- `bypassed_plan_gate: false` (const)
- `approved_for_execution: false` / `authority_mutation: false`
- Live path is opt-in; fixture remains the default
