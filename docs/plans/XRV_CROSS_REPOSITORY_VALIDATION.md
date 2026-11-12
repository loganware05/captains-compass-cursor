# XRV — Cross-Repository Engineering Intelligence Validation

> **W1 COMPLETE** (2026-11-11) — `xrv-release-integrity` (#261) merged [#262](https://github.com/loganware05/captains-compass-cursor/pull/262) @ `dece600` → **v1.83.1**.
> **W2 IN PROGRESS:** `xrv-readiness-assessor` (#263) — APPROVED → **v1.84.0**.
> Rollback (W1): `rollback/pre-xrv-release-integrity` @ `987a49c`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

## One-line summary

Prove NorthStar improves real engineering outcomes across independent pilot
repositories with shared evidence, maturity-aware readiness, and Captain-gated
learning—before expanding features or autonomy.

## Program pillars

1. **Release integrity** — docs and GitHub state agree; CI detects VERSION↔README drift
2. **Experience Evidence Records (EER)** — auditable issue→outcome cycles across repos
3. **Pilot A TrapHouse Kitchen** — payment safety + release confidence
4. **Pilot B bitcoin-data-collector** — paper continuity; live execution denied
5. **Pilot C PrizePicksBot** — transfer-learning after access/baseline
6. **Adaptive benefit** — held-out baseline vs experience-informed runs (later)
7. **Provider proofs** — live sandbox only when they serve the pilot (later)

## Operator surfaces (W1)

```bash
./scripts/northstar evidence drift --repo .
COMPASS_XRV_EER_ENABLED=1 \
  ./scripts/northstar evidence validate --repo . \
  --path .agent/evidence/xrv/eer-i6-cross-provider-fixture.json
```

## Week 1–2 exit criteria

- [x] NorthStar VERSION / README aligned (control PR)
- [x] Machine-checked release drift
- [x] EER schema + I6 reconstruction fixture
- [x] I1–I6 + #261 issues closed (Captain 2026-11-11)
- [ ] TrapHouse Slice 17 docs/evidence reconcile (PR [#37](https://github.com/loganware05/TrapHouseKitchen/pull/37))
- [ ] Bitcoin Pilot B continuity PR (#17)
- [x] Eight-pillar readiness assessor (#263) — implementing v1.84.0
- [ ] Independent auditor can reconstruct at least one full engineering cycle per pilot

## Explicit deferrals

- Specialized Model Level 3 (#237)
- Fully autonomous merge / production actions
- Standalone NorthStar application
- Live Sentry/Apify/T3/Scrimba/WorkOS until pilot-scoped plans approve

## Related

- Notion roadmap (Nov 2026): Cross-Repository Validation & Adaptive Intelligence
- Prior consolidation: N1–N5 complete on control plane
- I6 hermetic provider scorecard: v1.83.0 / #260
