# M25 validation — agent router wakeability

| Field | Value |
|---|---|
| Plan | `m25-agent-router-wakeability` (Captain-approved 2026-09-11) |
| Linear | OVA-19 |
| Origin | OVA-17 / NS-SKILL-001 |
| Branch | `cursor/ova-19-m25-agent-router-wakeability-05fd` |
| Baseline tag | `v1.29.0` |
| Control PR | https://github.com/loganware05/captains-compass-cursor/pull/134 (**MERGED**) |
| Control merge | `69e949413adb87d608dcce62beaeacc17ee63bda` @ 2026-09-11T18:37:46Z |
| Sandbox registry PR | https://github.com/loganware05/captain-compass-sandbox/pull/48 (**MERGED**) |
| Sandbox merge | `7404066a7db43752c2e71a0748d568d9cdc615ca` @ 2026-09-11T18:37:33Z |
| Linear | OVA-19 |

## Checks

| Check | Result |
|---|---|
| `python3 -m unittest tests.orchestrator.test_m25_agent_router_wakeability` | Pass (7) |
| Full `tests/orchestrator` unittest discover | Pass (289) |
| `scripts/doctor.sh` | Pass including `score-agent-routing.sh` |
| Captain merge | Confirmed via `gh pr view` |

## Regression covered

Expired pin with `availability=1.0` is ineligible / not dispatch-ready.
Wakeable agents remain selectable. Live probe can mark unreachable.

## Authority

Linear records only. Repository tests + this evidence are canonical.
