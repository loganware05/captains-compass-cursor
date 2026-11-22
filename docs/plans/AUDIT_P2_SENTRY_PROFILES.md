# Audit P2 Sentry Polish & COMPASS Profiles v0 (durable plan copy)

> **COMPLETE** — plan ID `audit-p2-sentry-profiles`.
> Issue [#288](https://github.com/loganware05/captains-compass-cursor/issues/288).
> PR [#289](https://github.com/loganware05/captains-compass-cursor/pull/289) merged `c069554`.
> Release [`v1.88.0`](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.88.0).
> Rollback `rollback/pre-audit-p2-sentry-profiles` @ `bb8f334`.
>
> Captain Approve 2026-11-21: Q1=yes, Q2=yes profiles, Q3=no T3, Q4=v1.88.0.

## Goal

Bounded audit P2: wire I1 Sentry `window_hours` into live queries; add
additive `COMPASS_PROFILE=core|integrations` v0. Defer specialized real eval, T3 live, B4 FIX/SUBMIT.

## Outcome

Shipped in **v1.88.0**. See root `IMPLEMENTATION_PLAN.md` (COMPLETE) and
`.agent/evidence/audit-p2-sentry-profiles/`.
