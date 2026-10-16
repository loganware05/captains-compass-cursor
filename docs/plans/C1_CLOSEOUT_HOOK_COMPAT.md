> **APPROVED** (2026-10-16) — Plan ID `c1-closeout-hook-compat`.
> Issue: [#201](https://github.com/loganware05/captains-compass-cursor/issues/201).
> Branch: `fix/201-c1-closeout-hook-compat` · Rollback `rollback/pre-c1-closeout-hook-compat`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# C1 Closeout + Hook Compat

Post-merge hygiene after Cognitive Core C1 (#200 / v1.60.0):

1. Commit live hook `from __future__ import annotations` (Python &lt;3.10)
2. Mark C1 COMPLETE in project memory
3. README version reconcile; Captain standing order (approve → commit → PR)
4. Patch release **v1.60.1**

Non-goals: C2–C7 product features (Notion sequence).

## Operator after merge

```bash
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain sync --repo .
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain status --repo .
```
