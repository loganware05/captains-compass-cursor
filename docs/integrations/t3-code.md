# T3 Code ExecutionAdapter (I2)

Gated NorthStar-owned execution surface for T3 Code threads. Fixture-first.
Never bypasses plan approval gates.

## Gates

```bash
COMPASS_T3_EXEC_ENABLED=1     # required
COMPASS_T3_EXEC_LIVE=1        # optional; live skeleton fail-closed in v1.79.0
```

## Commands

```bash
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 capabilities

COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 start \
  --plan-id i2-t3-execution-adapter \
  --objective "bounded task" \
  [--allow-fixture-plan]   # hermetic tests only

COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 status --execution-id ID
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 collect --execution-id ID
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 cancel --execution-id ID
COMPASS_T3_EXEC_ENABLED=1 ./scripts/northstar t3 list
```

`start` requires `IMPLEMENTATION_PLAN.md` Plan ID match and status in
APPROVED / IN PROGRESS / VALIDATING, unless `--allow-fixture-plan`.

## Storage

Runs under `.agent/executions/t3/`. Overseer snapshots expose `execution_refs`.

## Authority

- `bypassed_plan_gate: false` (const)
- `approved_for_execution: false` / `authority_mutation: false`
- Live MCP transport remains a future injectable; default is fixture
