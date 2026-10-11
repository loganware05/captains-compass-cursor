> **APPROVED / IMPLEMENTING** (2026-10-11) — Captain approved; product impl on
> `feature/OVA-66-m50-policy-promotion-lifecycle` (v1.55.0).
> Active root plan: `IMPLEMENTATION_PLAN.md` (Plan ID `m50-policy-promotion-lifecycle`).

# M50 — Policy / Instruction Promotion Lifecycle

Spec source: [Notion — Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M50 section)

Linear: [OVA-66](https://linear.app/ovaltechnologysolutions/issue/OVA-66/m50-policy-instruction-promotion-lifecycle-v1550)

Notion plan mirror: [M50 Implementation Plan](https://app.notion.com/p/3f6e6a901c4381b4b7b3f04d2f848aa9)

Linear project: [NorthStar Behavioral Intelligence Loop](https://linear.app/ovaltechnologysolutions/project/northstar-behavioral-intelligence-loop-e24174b3f1ef)

Prerequisite: M49 shipped (#187 / v1.49.0); control repo baseline **v1.54.0** (AHF-P06 #192).

## One-line summary

Governed Policy/instruction promotion lifecycle via `northstar policy` —
sandbox → shadow → Captain-approved Active/Proven; no auto `.cursor/` mutation.

## Baseline

v1.54.0 @ `dad671f` → release **v1.55.0**

## Resolved decisions (Captain — 2026-10-11)

1. Top-level `northstar policy`
2. New `COMPASS_POLICY_PROMOTE_ENABLED` (default off)
3. Active = compose-eligible only under `COMPASS_POLICY_APPLY_ENABLED`
4. Materialize proposals only (no auto `.cursor/` copy)
5. Proven threshold ≥2 successful M46 evaluations
6. v1.55.0

## Operator surface

```bash
COMPASS_POLICY_PROMOTE_ENABLED=1 ./scripts/northstar policy list --repo .
COMPASS_POLICY_PROMOTE_ENABLED=1 ./scripts/northstar policy promote \
  --instruction-id <id> --to sandbox_evaluated --prompt-eval-report <id> --repo .
COMPASS_POLICY_PROMOTE_ENABLED=1 ./scripts/northstar policy shadow \
  --policy-id <id> --repo .
COMPASS_POLICY_PROMOTE_ENABLED=1 ./scripts/northstar policy promote \
  --policy-id <id> --to active --captain-approved --repo .
```

## Non-goals

- M51 Project Overseer
- AHF live execution enablement
- Auto Skill/routing/authority mutation
