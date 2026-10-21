> **AWAITING APPROVAL** (2026-10-21) — Plan ID `read-only-persistent-oversight`.
> Issue: [#225](https://github.com/loganware05/captains-compass-cursor/issues/225).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# Read-Only Persistent Oversight

Prerequisite: E2E Cognitive Core evaluation shipped (**v1.67.0** / #224).

## One-line summary

Opt-in post-merge (or explicit) compose of brain sync + Overseer snapshot /
compare / reconcile proposals — drift detection only; never auto-rewrites memory
or expands authority.

## Proposed operator surface

```bash
COMPASS_STATUS_ENABLED=1 COMPASS_BRAIN_ENABLED=1 \
  ./scripts/northstar oversight run --repo . [--since SHA] [--enable-gates]
# alias: northstar status post-merge …
```

## Non-goals

Auto-apply reconcile patches; automatic merges; Specialized Model training;
continuous unsupervised self-training; HTTP oversight daemon required for CI.
