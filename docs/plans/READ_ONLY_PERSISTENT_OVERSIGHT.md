> **COMPLETE** (2026-10-21) — Merged [#227](https://github.com/loganware05/captains-compass-cursor/pull/227)
> → `main` @ `f5bbf24` (**v1.68.0**). Plan ID `read-only-persistent-oversight`.
> Issue: [#225](https://github.com/loganware05/captains-compass-cursor/issues/225) (closed).
> Rollback: `rollback/pre-read-only-persistent-oversight` @ `c5d435e`.
> Evidence: `.agent/evidence/read-only-persistent-oversight/`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Read-Only Persistent Oversight

Opt-in post-merge / on-demand compose of brain sync + Overseer
snapshot/compare/reconcile proposals — shipped **v1.68.0**.

## Operator surface

```bash
./scripts/run-oversight.sh --repo-root . --enable-gates [--since SHA]
./scripts/northstar oversight run --repo . --enable-gates
./scripts/northstar status post-merge --repo . --enable-gates
```

## Next

Specialized Model Level 0 (#228) — **AWAITING APPROVAL**.
