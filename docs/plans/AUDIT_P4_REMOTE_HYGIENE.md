# Audit P4 Remote Hygiene (durable plan copy)

> **APPROVED / IN PROGRESS** — plan ID `audit-p4-remote-hygiene`.
> Issue [#294](https://github.com/loganware05/captains-compass-cursor/issues/294).
> Branch `docs/294-audit-p4-remote-hygiene`. Rollback
> `rollback/pre-audit-p4-remote-hygiene` @ `28bd0c2`.
>
> Captain Approve 2026-11-22: Q1=yes, Q2=dry-run merged allowlist, Q3=yes
> auto-delete, Q4=no XRV/Bend.

## Goal

Prune stale remote heads, enable `delete_branch_on_merge`, archive obsolete
P1/P2 awaiting stubs. Defer T3/specialized/B4/XRV ops-verified/Bend #278.

## Baseline

`origin/main` @ `28bd0c2` / **v1.89.0**. Release **v1.89.1**.

## Outcome (pre-PR)

- Heads **204 → 5**; 199 merged remotes deleted
- `delete_branch_on_merge=true`
- Stubs moved to `docs/plans/archive/`
