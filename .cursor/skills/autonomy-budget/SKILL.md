---
name: autonomy-budget
description: Tracks per-plan autonomy budgets and stops with a Budget Stop Report when limits are hit
---

# Autonomy Budget

## Use this Skill when

An implementation plan is **APPROVED** and autonomous execution begins, or whenever
an iteration / validation cycle completes, or when any budget limit may have been reached.

## Inputs

- Approved `IMPLEMENTATION_PLAN.md` (Autonomy Budget section)
- Plan ID (from plan metadata)
- Current counters (iterations, failed validation cycles, elapsed time, estimated cost)

## Procedure

1. When the plan status becomes **APPROVED**, create
   `.agent/budgets/<plan-id>.md` from `templates/agent/BUDGET_LEDGER.md`
   (or copy from `.agent/budgets/_templates/BUDGET_LEDGER.md` if installed).
   Fill limits from the plan’s Autonomy Budget section.
2. After each implementation + validation cycle, update the ledger:
   - Increment `iterations_used`
   - If validation failed, increment `failed_validation_cycles`
   - Update `elapsed_minutes` and `estimated_cost_usd` (label estimates clearly)
   - Append a one-line cycle note under the log section
3. Before starting another cycle, compare used vs maximum for every limit.
4. If **any** limit is reached or exceeded:
   - Stop further implementation
   - Write a Budget Stop Report under
     `.agent/evidence/<plan-id-or-slug>/BUDGET_STOP_REPORT.md`
     using `templates/agent/BUDGET_STOP_REPORT.md`
   - Set plan/progress notes to reflect the stop
   - Ask the Captain for the next action (raise budget, narrow scope, or abandon)
5. At phase boundaries, append a short note under `.agent/sessions/` using
   `templates/agent/SESSION_NOTE.md` (or `.agent/budgets/_templates/` siblings when
   installed). Keep machine traces under `.agent/runs/` if used.
6. Never raise budget limits unilaterally. Never weaken tests to stay under budget.

## Ledger path

```text
.agent/budgets/<plan-id>.md
```

Private cost notes (optional): `.agent/budgets/private/` (gitignored pattern).

## Output

- Updated budget ledger
- Budget Stop Report when stopped
- Clear Captain-facing recommendation

## Prohibited actions

- Continuing past any budget limit without a Budget Stop Report and Captain decision
- Hiding failed validation cycles
- Storing secrets or `.env` contents in ledgers or stop reports
