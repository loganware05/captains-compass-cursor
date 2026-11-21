# Audit P0 Governance & Hygiene (durable plan copy)

> **COMPLETE** — plan ID `audit-p0-governance-hygiene`. Merged via PR #281 @ `e3debd4`
> (v1.87.1). Budget: `.agent/budgets/audit-p0-governance-hygiene.md`. Source: cloud agent
> `bc-22bbacc4-5283-4fa1-a382-29baec9fff57` (NorthStar full engineering audit canvas,
> 2026-11-20/21).

## Goal

Remediate the audit’s three **P0** items first: Finding 001 policy entry bypass, test suite
writes that dirty git, and stale post-merge governance (#279 merged / #247 & #278 still open).

## In scope

1. Force `ensure_policy_for_instruction()` to create policies at `candidate` only.
2. Isolate test writers (N3 LATEST_*, train-metrics, `.agent/tmp-*`) into temp dirs.
3. Closeout docs/issues per Captain decisions on ADR-110 / #278 / #247.

## Out of scope

P1 doctor flake & UI CI; P2 live integrations / specialized eval; P3 XRV ops drill & OpenUI
viewer; deferred AHF live / L3 / hosted vector DB.

## Branch / rollback

- Branch: `feature/<issue>-audit-p0-governance-hygiene` from `main`
- Rollback tag: `rollback/pre-audit-p0-governance-hygiene`

See root `IMPLEMENTATION_PLAN.md` for full acceptance criteria, task graph, and open questions.
