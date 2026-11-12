# XRV — Cross-Repository Engineering Intelligence Validation

> **IN PROGRESS** (2026-11-10) — Control-plane Week 1 plan `xrv-release-integrity` (#261).
> Proposed release: **v1.83.1**.
> Rollback: `rollback/pre-xrv-release-integrity` @ `987a49c`.
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
- [ ] TrapHouse Slice 17 docs/evidence reconcile (companion plan; handoff thread)
- [ ] Independent auditor can reconstruct at least one full engineering cycle

## Explicit deferrals

- Specialized Model Level 3 (#237)
- Fully autonomous merge / production actions
- Standalone NorthStar application
- Live Sentry/Apify/T3/Scrimba/WorkOS until pilot-scoped plans approve

## Related

- Notion roadmap (Nov 2026): Cross-Repository Validation & Adaptive Intelligence
- Prior consolidation: N1–N5 complete on control plane
- I6 hermetic provider scorecard: v1.83.0 / #260
