# Implementation Plan — T3 MCP/HTTP Live Adapter

- Status: **COMPLETE**

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `t3-mcp-live-adapter` |
| Issue | [#300](https://github.com/loganware05/captains-compass-cursor/issues/300) |
| Baseline | `origin/main` @ `5a76f27` / product **v1.89.2** @ `4d17597` |
| Branch | `feature/300-t3-mcp-live-adapter` |
| Worktree | `/Users/loganware/Documents/Personal/Code/captains-compass-t3-live` |
| Rollback | `rollback/pre-t3-mcp-live-adapter` @ `5a76f27` |
| Proposed release | **v1.90.0** |
| Created | 2026-11-22 |
| Approved | 2026-11-22 (Captain: Approve; Q1–Q4 recommended defaults) |

Budget: `.agent/budgets/t3-mcp-live-adapter.md`  
Durable copy: `docs/plans/T3_MCP_LIVE_ADAPTER.md`  
Evidence: `.agent/evidence/t3-mcp-live-adapter/`

## Approval record

- Captain replied **Approve** on 2026-11-22.
- Defaults accepted: ship T3 live adapter; allowlisted ops only; hermetic CI +
  opt-in live; defer specialized/B4.

## Request

Finish the I2 T3 ExecutionAdapter live seam: inject an MCP/HTTP transport so
`LiveT3ExecutionAdapter` can run `capabilities|start|status|collect|cancel`
behind dual gates, with hermetic `RecordingTransport` tests.

## Scope delivered

- [x] `orchestrator/integrations/t3/client.py` HTTPS JSON allowlist client
- [x] `LiveT3ExecutionAdapter` transport injection + live lifecycle
- [x] Service live status/collect/cancel wiring
- [x] Hermetic unit tests (RecordingTransport)
- [x] Docs / ADR-115 / VERSION 1.90.0 / doctor client + fixture-default check

## Validation

- Unit: `python3 -m unittest tests.orchestrator.test_i2_t3_execution_adapter -v`
- Doctor + `tests/run.sh` (in progress)

## Rollback

```bash
git checkout rollback/pre-t3-mcp-live-adapter
```
