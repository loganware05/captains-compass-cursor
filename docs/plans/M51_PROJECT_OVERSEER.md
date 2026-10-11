> **APPROVED / IMPLEMENTED** (2026-10-11) — Captain approved; v1.56.0 on branch
> `feature/OVA-67-m51-project-overseer`.
> Active root plan: `IMPLEMENTATION_PLAN.md` (Plan ID `m51-project-overseer`).

# M51 — Kimi K3 Project Overseer

Spec source: [Notion — Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M51 section)

Linear: [OVA-67](https://linear.app/ovaltechnologysolutions/issue/OVA-67/m51-kimi-k3-project-overseer-v1560)

Notion plan mirror: [M51 Implementation Plan](https://app.notion.com/p/3f6e6a901c438131b2aacb3b7e1224c2)

Prerequisite: M50 merged (#193 / v1.55.0).

## One-line summary

Read-oriented Project Overseer via `northstar status` — snapshot / explain /
compare / reconcile proposals; no authority mutation.

## Baseline

v1.55.0 @ `5d108db` → release **v1.56.0**

## Resolved decisions (Captain — 2026-10-11)

1. Top-level `northstar status`
2. New `COMPASS_STATUS_ENABLED` (default off)
3. Deterministic hermetic drift first (+ stub provider interface)
4. Persist under `.agent/status/`
5. Reconcile proposals only (no auto memory rewrite)
6. v1.56.0

## Operator surface

```bash
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status explain --repo .
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status compare --since HEAD~5 --repo .
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status reconcile --repo .
```

## Non-goals

- Live Kimi required for CI
- Auto-approve / promote / merge / deploy
- Silent PROJECT_CONTEXT rewrites
