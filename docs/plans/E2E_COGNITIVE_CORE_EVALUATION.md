> **COMPLETE** (2026-10-21) — Merged [#224](https://github.com/loganware05/captains-compass-cursor/pull/224)
> → `main` @ `05dcfba` (**v1.67.0**). Plan ID `e2e-cognitive-core-evaluation`.
> Issue: [#222](https://github.com/loganware05/captains-compass-cursor/issues/222) (closed).
> Rollback: `rollback/pre-e2e-cognitive-core-evaluation` @ `bb1b5b9`.
> Evidence: `.agent/evidence/e2e-cognitive-core-evaluation/`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# E2E Cognitive Core Evaluation (C1–C7)

Hermetic C1–C7 evaluation harness with schema-validated report and measured
baselines — shipped **v1.67.0**.

## Operator surface

```bash
./scripts/run-cognitive-core-e2e.sh --repo-root . --enable-gates --mode hermetic
./scripts/northstar cognitive e2e --repo . --enable-gates
```

## Next

Read-only persistent oversight (#225) — **AWAITING APPROVAL**.
