# Security review — c5-cognitive-core-adaptive-routing

| Item | Assessment |
|---|---|
| Authority expansion | None — schema const false |
| Live model binding | None — `auto_switched: false`; advisory proposal only |
| Spend | No cloud spend path; budget fields are hints |
| Secrets | Objective treated as local text |
| Network | Evaluate requires no network; route compose is local |
| Gate | Fail-closed without `COMPASS_ROUTE_ENABLED` |

Residual risk: low. Operators must not treat route proposals as automatic model switches.
