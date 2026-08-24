---
name: bounded-autonomy
description: Applies Captain-approved routing weight proposals under autonomy budget (Level 3 bounded)
---

# Bounded Autonomy

## Use this Skill when

The Captain has reviewed an experience-routing proposal and wants to **apply**
matcher weight suggestions under an autonomy budget (Milestone 4 Level 3).

## Inputs

- Routing proposal JSON under `.agent/routing/proposals/` with
  `captain_approved: true` (Captain sets this flag explicitly)
- Autonomy budget ledger path (recommended)

## Procedure

1. Generate or locate a proposal (`experience-routing` Skill). Confirm
   `auto_apply` remains `false`.
2. Captain edits the proposal to set `"captain_approved": true`.
3. Apply once under budget:

   ```bash
   ./scripts/apply-routing-proposal.sh \
     --proposal .agent/routing/proposals/<id>.json \
     --budget .agent/budgets/<plan-id>.md
   ```

4. Review audit under `.agent/routing/applied/` and re-run evals.
5. Rollback if needed by restoring `orchestrator/matcher/weights.json` defaults
   (or `rollback/pre-m4-persistent-roles-bounded-autonomy`).

## Output

- Updated `orchestrator/matcher/weights.json`
- Audit record under `.agent/routing/applied/`
- Incremented weight-apply counter on the budget ledger

## Prohibited actions

- Applying without `captain_approved: true`
- Auto-applying from proposal generation
- Mutating Skills or `.cursor/agents/` from this Skill
- Exceeding the plan's maximum weight-apply operations
