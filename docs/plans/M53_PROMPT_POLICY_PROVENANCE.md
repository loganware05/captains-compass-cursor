> **APPROVED** (2026-10-11) — Captain: "I approve".
> Active root plan: `IMPLEMENTATION_PLAN.md` (Plan ID `m53-prompt-policy-provenance`).

# M53 — Prompt/Policy Provenance + Behavior Exemplars

Spec source: [Notion — Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (Provenance + Exemplars)

Linear: [OVA-69](https://linear.app/ovaltechnologysolutions/issue/OVA-69/m53-promptpolicy-provenance-behavior-exemplars-v1580)

Prerequisite: M52 merged (#195 / v1.57.0).

## One-line summary

Unified execution provenance ledger + positive/negative behavior exemplars;
proposal/read-only; no authority mutation.

## Baseline

v1.57.0 @ `448ac25` → release **v1.58.0**

## Resolved decisions

1. Provenance ledger + exemplar store + CLI
2. `COMPASS_PROVENANCE_ENABLED` (default off)
3. Persist under `.agent/evaluations/behavior/provenance/` + `.agent/examples/`
4. Best-effort emit from evaluate when gated; compose fields via capture when available
5. Exemplars never auto-promote
6. v1.58.0

## Deferred

- AHF-P07+ (gated)
- Scheduled Overseer automations

## Operator surface

```bash
COMPASS_PROVENANCE_ENABLED=1 ./scripts/northstar provenance capture --execution-id <id> --repo .
COMPASS_PROVENANCE_ENABLED=1 ./scripts/northstar examples draft --polarity positive --evaluation-id <id> --repo .
```

## Evidence

`.agent/evidence/m53-prompt-policy-provenance/VALIDATION.md`
