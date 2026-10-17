# Security review — c4-cognitive-core-adaptive-loop

| Item | Assessment |
|---|---|
| Authority expansion | None — schema const false; Learning Review cannot approve plans |
| Promotion | Draft proposals only (`auto_promoted: false`); no Skill/Policy install |
| Secrets | Objective/notes treated as local text; no new secret surfaces |
| Network | No network required |
| Persistence | Cycle JSON under `.agent/cycles/` (gitignored runtime); telemetry via existing stores |
| Gate | Fail-closed without `COMPASS_CYCLE_ENABLED`; begin also needs assess gate |

Residual risk: low. Cycle friction scores are advisory and must not substitute for Captain approval.
