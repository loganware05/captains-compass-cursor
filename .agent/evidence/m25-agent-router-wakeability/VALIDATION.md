# M25 validation — agent router wakeability

| Field | Value |
|---|---|
| Plan | `m25-agent-router-wakeability` (Captain-approved 2026-09-11) |
| Linear | OVA-19 |
| Origin | OVA-17 / NS-SKILL-001 |
| Branch | `cursor/ova-19-m25-agent-router-wakeability-05fd` |
| Baseline tag | `v1.29.0` |

## Checks

| Check | Result |
|---|---|
| `python3 -m unittest tests.orchestrator.test_m25_agent_router_wakeability` | Pass (7) |
| Full `tests/run.sh` orchestrator unittest | (recorded at PR time) |
| `scripts/doctor.sh` | Pass including `score-agent-routing.sh` |

## Regression covered

Expired pin with `availability=1.0` is ineligible / not dispatch-ready.
Wakeable agents remain selectable. Live probe can mark unreachable.

## Authority

Linear records only. Repository tests + this evidence are canonical.
