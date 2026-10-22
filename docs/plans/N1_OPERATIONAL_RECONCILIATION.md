> **AWAITING APPROVAL** (2026-10-22) — Plan ID `n1-operational-reconciliation`.
> Baseline: **v1.71.0** @ `15e8866` / [#235](https://github.com/loganware05/captains-compass-cursor/pull/235).
> Proposed release: **v1.71.1**.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.
> Issue: Captain files GitHub issue before or on approval (agent cannot create issues).
> Related: Specialized Model Level 3 remains **DEFERRED** (see
> [`SPECIALIZED_MODEL_LEVEL_3.md`](SPECIALIZED_MODEL_LEVEL_3.md)).

# N1 — Operational Reconciliation & Development Closeout

Consolidation checkpoint after Cognitive Core C1–C7, persistent oversight,
and Specialized Model Levels 0–2.

## One-line summary

Evidence-grounded reconciliation of open issues, plans, operator docs, and
release records; optional Overseer closeout-readiness report; N2/N3 follow-on
stubs; Level 3 GPU expansion deferred until justified.

## Operator surfaces (post-implementation)

```bash
# Existing
./scripts/northstar status snapshot|explain|compare|reconcile --repo .
./scripts/northstar oversight run --repo . --enable-gates

# Proposed (default if approved)
./scripts/northstar status closeout --repo .
```

## Seed ledger (pre-implementation snapshot — verify on execute)

| Tracker | Current interpretation | Recommended disposition |
|---|---|---|
| [#220](https://github.com/loganware05/captains-compass-cursor/issues/220) | PR [#221](https://github.com/loganware05/captains-compass-cursor/pull/221) merged | Verify acceptance → close |
| [#222](https://github.com/loganware05/captains-compass-cursor/issues/222) | PR [#224](https://github.com/loganware05/captains-compass-cursor/pull/224) merged | Verify acceptance → close |
| [#164](https://github.com/loganware05/captains-compass-cursor/issues/164) | Product install not proven at current VERSION | Keep for **N2** / still_actionable |
| [#169](https://github.com/loganware05/captains-compass-cursor/issues/169) | Shell forge gate — reassess residual | Verify vs code → close or residual |
| [#170](https://github.com/loganware05/captains-compass-cursor/issues/170) | Agentic Security Phase B | Verify allowlist/tests → close or residual |
| [#147](https://github.com/loganware05/captains-compass-cursor/issues/147) | Opt-in GitHub draft reviews | Verify docs/tests → close or residual |
| [#146](https://github.com/loganware05/captains-compass-cursor/issues/146) | Intent packs + templates | Reconcile with merged review track |
| [#144](https://github.com/loganware05/captains-compass-cursor/issues/144) | Code Reviewer specialist composition | Verify acceptance → close |

Do **not** auto-close from this table alone.

## Follow-on

- **N2** — Product Integration Validation (`docs/plans/N2_PRODUCT_INTEGRATION_VALIDATION.md`)
- **N3** — Adaptive Intelligence Validation (`docs/plans/N3_ADAPTIVE_INTELLIGENCE_VALIDATION.md`)
- **Level 3** — DEFERRED until N1–N3 + Level 0–2 proof-of-value

## Non-goals

Level 3 implementation, paid GPU jobs, Skill/policy auto-promotion, N2/N3
execution, silent issue closure.
