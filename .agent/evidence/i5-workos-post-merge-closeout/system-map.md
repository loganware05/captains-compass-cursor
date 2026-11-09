# Project Overseer system map (generated)

> Non-canonical Overseer artifact under `.agent/status/`.
> Does **not** replace `PROJECT_CONTEXT.md`, ADRs, or `PROGRESS.md`.

- Snapshot: `psnap-a827ae6b958c`
- NorthStar version (observed): `1.82.0`
- Repository SHA (observed): `d2e0f37ae7bced7d5801022e9907a0857ec18bc3`
- Plan ID (documented): `i5-workos-identity`
- Plan status (documented): `**COMPLETE**`
- Skills on disk (observed): `47`
- Skills in docs (documented): `47`
- Provenance refs (observed): `4`
- Incident refs (external): `2`
- Conversation refs (external): `0`
- Execution refs (observed): `2`
- Research refs (external): `1`
- Explainer refs (external): `1`
- Identity refs (external): `1`

## Findings

- [info/observed] All required project memory docs are present.
- [info/external] Observed 2 Sentry incident evidence packet(s) under .agent/incidents/sentry/.
- [info/observed] Observed 2 T3 ExecutionAdapter run(s) under .agent/executions/t3/.
- [info/external] Observed 1 Apify research packet(s) under .agent/research/apify/.
- [info/external] Observed 1 Scrimba explainer packet(s) under .agent/explainers/.
- [info/external] Observed 1 WorkOS identity packet(s) under .agent/identity/workos/.

## Development evidence

- [incident/warning] `sentry-fixture-org-fixture-project-1002` — TimeoutError: upstream payment gateway
- [incident/error] `sentry-fixture-org-fixture-project-1001` — TypeError: cannot read property of undefined
- [t3/started] `t3-exec-39a769032ba0` plan=`i2-t3-execution-adapter`
- [t3/started] `t3-exec-944fc68a5b67` plan=`i2-t3-execution-adapter`
- [apify/fixture] `apify-research-24fb954d8898` query=`web research`
- [scrimba/fixture] `scrimba-explain-768f714e9d6a` topic=`How NorthStar approval gates work`
- [workos/fixture] `workos-identity-7054ac8270f0` org=`org_fixture_northstar`

## Authority

- `approved_for_execution`: false
- `authority_mutation`: false
- Reconcile proposals remain proposal-only.
- Incident/conversation/research/explainer/identity refs are external; T3 refs are observed. WorkOS roles never grant Captain approval.
