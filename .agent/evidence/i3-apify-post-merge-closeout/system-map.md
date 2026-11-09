# Project Overseer system map (generated)

> Non-canonical Overseer artifact under `.agent/status/`.
> Does **not** replace `PROJECT_CONTEXT.md`, ADRs, or `PROGRESS.md`.

- Snapshot: `psnap-4e494369c9d6`
- NorthStar version (observed): `1.80.0`
- Repository SHA (observed): `773e21ab727efa698e08ceeefc0b9819fb9d6535`
- Plan ID (documented): `i3-apify-ti-provider`
- Plan status (documented): `**COMPLETE**`
- Skills on disk (observed): `47`
- Skills in docs (documented): `47`
- Provenance refs (observed): `4`
- Incident refs (external): `2`
- Conversation refs (external): `0`
- Execution refs (observed): `2`
- Research refs (external): `1`

## Findings

- [info/observed] All required project memory docs are present.
- [info/external] Observed 2 Sentry incident evidence packet(s) under .agent/incidents/sentry/.
- [info/observed] Observed 2 T3 ExecutionAdapter run(s) under .agent/executions/t3/.
- [info/external] Observed 1 Apify research packet(s) under .agent/research/apify/.

## Development evidence

- [incident/warning] `sentry-fixture-org-fixture-project-1002` — TimeoutError: upstream payment gateway
- [incident/error] `sentry-fixture-org-fixture-project-1001` — TypeError: cannot read property of undefined
- [t3/started] `t3-exec-39a769032ba0` plan=`i2-t3-execution-adapter`
- [t3/started] `t3-exec-944fc68a5b67` plan=`i2-t3-execution-adapter`
- [apify/fixture] `apify-research-24fb954d8898` query=`web research`

## Authority

- `approved_for_execution`: false
- `authority_mutation`: false
- Reconcile proposals remain proposal-only.
- Incident/conversation/research refs are external; T3 refs are observed.
