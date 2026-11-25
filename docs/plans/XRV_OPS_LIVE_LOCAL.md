# XRV Ops Live-Local Smoke

> **APPROVED** — plan ID `xrv-ops-live-local`. Issue [#316](https://github.com/loganware05/captains-compass-cursor/issues/316).
> Budget: `.agent/budgets/xrv-ops-live-local.md`. Active gate: root `IMPLEMENTATION_PLAN.md`.
> Baseline: `origin/main` @ `08c897f` / **v1.95.0**. Rollback: `rollback/pre-xrv-ops-live-local`.

Local operational smoke against a real tip SHA (doctor + reconstruct). No production deploy.
`live_deploy` remains false unless Captain opts in later.
