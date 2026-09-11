# M26 validation — Cursor Cloud wakeability probe

| Field | Value |
|---|---|
| Plan | Captain-directed 2026-09-11 (after v1.29.1) |
| Module | `orchestrator/routing/cloud_wakeability_probe.py` |
| CLI | `score-agent-routing.sh --cloud-agents-json` |

## Checks

| Check | Result |
|---|---|
| M26 unit tests | Pass (7) |
| M25 unit tests still green | Pass (7) |
| Live probe smoke (sandbox registry + Cloud snapshot) | Pass — historical pin `expired` via `live_probe`; `dispatch_ready=false` |

## Smoke artifacts

- `live-probe-smoke-cloud-agents.json`
- `live-probe-smoke-decision.json`

## Authority

Linear records only. Repository evidence is canonical.
