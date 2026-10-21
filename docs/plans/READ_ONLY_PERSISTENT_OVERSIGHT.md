> **PR OPEN** — [#227](https://github.com/loganware05/captains-compass-cursor/pull/227) / [#225](https://github.com/loganware05/captains-compass-cursor/issues/225).
> Plan ID `read-only-persistent-oversight`.
> Branch: `cursor/225-read-only-persistent-oversight-3ec1`.
> Rollback: `rollback/pre-read-only-persistent-oversight` @ `c5d435e`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Read-Only Persistent Oversight

Opt-in post-merge / on-demand compose of brain sync + Overseer
snapshot/compare/reconcile proposals — never auto-applies.

## Operator surface

```bash
./scripts/run-oversight.sh --repo-root . --enable-gates [--since SHA]
./scripts/northstar oversight run --repo . --enable-gates
./scripts/northstar status post-merge --repo . --enable-gates
```

Optional hook snippet: `docs/guides/oversight-post-merge-hook.md`.
