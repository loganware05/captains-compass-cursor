# T3 MCP/HTTP Live Adapter (durable plan copy)

> Plan ID `t3-mcp-live-adapter` — **COMPLETE**. Active gate: root
> `IMPLEMENTATION_PLAN.md`. Budget: `.agent/budgets/t3-mcp-live-adapter.md`.
> Issue [#300](https://github.com/loganware05/captains-compass-cursor/issues/300).

## Goal

Inject HTTPS JSON transport into I2 `LiveT3ExecutionAdapter` so live
capabilities/start/status/collect/cancel work behind dual gates, with hermetic
RecordingTransport tests. Defer specialized, B4 FIX→SUBMIT, XRV ops-verified,
Bend #278.

## Baseline

`origin/main` @ `5a76f27` / **v1.89.2**. Proposed **v1.90.0**.
Rollback: `rollback/pre-t3-mcp-live-adapter` @ `5a76f27`.

## Live contract

| Op | HTTPS | T3 MCP |
|---|---|---|
| capabilities | `GET /v1/capabilities` | `orchestrator_capabilities` |
| start | `POST /v1/threads` | `t3_thread_launch` |
| status/collect | `GET /v1/threads/{id}` | `t3_thread_read` |
| cancel | `POST /v1/threads/{id}/interrupt` | `t3_thread_interrupt` |
