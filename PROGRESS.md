# Progress

## Current status

**C7 Cognitive Core — Training bridge — PR OPEN**
[#219](https://github.com/loganware05/captains-compass-cursor/pull/219)
on `cursor/217-c7-training-bridge-64df` (**v1.66.0**).
Issue [#217](https://github.com/loganware05/captains-compass-cursor/issues/217).
Plan ID `c7-cognitive-core-training-bridge` **APPROVED** 2026-10-19.

| Item | Value |
|---|---|
| On main | **v1.65.0** C6 closeout (#218) @ `f16e8bb` |
| Active plan | `c7-cognitive-core-training-bridge` **PR #219** |
| Branch | `cursor/217-c7-training-bridge-64df` @ `49ddcf4` |
| Rollback | `rollback/pre-c7-cognitive-core-training-bridge` @ `f16e8bb` |
| Next | Captain merge #219 |

## Cognitive Core track

| Milestone | Status |
|---|---|
| C1 — Source of Truth | **Complete** (#200 / v1.60.0); closeout v1.60.1 |
| C2 — Memory and Retrieval | **Complete** (#204 / v1.61.0) |
| C3 — Difficulty and capability fit | **Complete** (#207 / v1.62.0) |
| C4 — Adaptive Development Loop | **Complete** (#210 / v1.63.0) |
| C5 — Adaptive routing | **Complete** (#213 / v1.64.0) |
| C6 — REA deep analysis | **Complete** (#216 / v1.65.0) |
| C7 — Training bridge | **PR open** ([#219](https://github.com/loganware05/captains-compass-cursor/pull/219) / v1.66.0) |

## Operator (C1–C7)

```bash
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain sync --repo .
COMPASS_ASSESS_ENABLED=1 ./scripts/northstar assess project --objective "…" --repo .
COMPASS_CYCLE_ENABLED=1 COMPASS_ASSESS_ENABLED=1 \
  ./scripts/northstar cycle begin --objective "…" --repo .
COMPASS_ROUTE_ENABLED=1 ./scripts/northstar model route --objective "…" --repo .
COMPASS_REA_ENABLED=1 ./scripts/northstar rea investigate \
  --target PATH --question "…" --repo .
COMPASS_TRAIN_BRIDGE_ENABLED=1 ./scripts/northstar train export \
  --from experiences --export-authorized --secrets-redacted-ack \
  --license-reviewed --pii-reviewed --specialized-model-handoff-ack --repo .
COMPASS_TRAIN_BRIDGE_ENABLED=1 ./scripts/northstar train review \
  --export-id ID --repo .
```

## Standing order (Captain — 2026-10-13)

When the Captain approves an `IMPLEMENTATION_PLAN.md`, the First Mate shall
**implement → validate → commit → open PR** without a separate ask. Merge remains Captain-only.

## Recently completed

- **C6 closeout / #218** — memory reconcile + C7 plan
- **C6 / #216** — Cognitive Core REA / `rea investigate` (v1.65.0)
- **C5 closeout / #215** — memory reconcile + C6 plan
- **C5 / #213** — Cognitive Core adaptive routing (v1.64.0)

## Blockers

None.
