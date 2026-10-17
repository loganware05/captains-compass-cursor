# Progress

## Current status

**C5 Cognitive Core — Adaptive routing** implementing on
`cursor/211-c5-adaptive-routing-64df` after Captain approval (2026-10-17).
Baseline **v1.63.0** @ `d8f1ac4`; target **v1.64.0**.

| Item | Value |
|---|---|
| On main | **v1.63.0** C4 + closeout (#210 / #212) @ `d8f1ac4` |
| Active plan | `c5-cognitive-core-adaptive-routing` **APPROVED** |
| Issue | [#211](https://github.com/loganware05/captains-compass-cursor/issues/211) |
| Branch | `cursor/211-c5-adaptive-routing-64df` |
| PR | [#213](https://github.com/loganware05/captains-compass-cursor/pull/213) (draft) |
| Rollback | `rollback/pre-c5-cognitive-core-adaptive-routing` @ `d8f1ac4` |
| Next | Captain merge of #213 |

## Cognitive Core track

| Milestone | Status |
|---|---|
| C1 — Source of Truth | **Complete** (#200 / v1.60.0); closeout v1.60.1 |
| C2 — Memory and Retrieval | **Complete** (#204 / v1.61.0) |
| C3 — Difficulty and capability fit | **Complete** (#207 / v1.62.0) |
| C4 — Adaptive Development Loop | **Complete** (#210 / v1.63.0) |
| C5 — Adaptive routing | **PR ready** (#211 / v1.64.0) |
| C6 — REA deep analysis | Deferred |
| C7 — Training bridge | Deferred |

## Operator (C1–C5)

```bash
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain sync --repo .
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain context --query "…" --repo .
COMPASS_ASSESS_ENABLED=1 ./scripts/northstar assess project --objective "…" --repo .
COMPASS_CYCLE_ENABLED=1 COMPASS_ASSESS_ENABLED=1 \
  ./scripts/northstar cycle begin --objective "…" --repo .
COMPASS_ROUTE_ENABLED=1 ./scripts/northstar model route --objective "…" --repo .
COMPASS_ROUTE_ENABLED=1 ./scripts/northstar model evaluate --repo .
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **C4 closeout / #212** — memory reconcile + C5 plan
- **C4 / #210** — Cognitive Core adaptive cycle / `cycle` + `learning review` (v1.63.0)
- **C3 closeout / #209** — memory reconcile + C4 plan
- **C3 / #207** — Cognitive Core difficulty / `assess project` (v1.62.0)

## Blockers

None.
