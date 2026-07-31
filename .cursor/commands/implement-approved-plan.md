Implement only an **APPROVED** Captain's Compass plan.

1. Confirm `IMPLEMENTATION_PLAN.md` status is **APPROVED** with an approval record. If not, refuse and tell the Captain to run `/plan-feature` or approve the plan first.
2. Load Skills as needed: `worktree-orchestration`, `autonomy-budget`, tech Skills for the stack, `source-code-context` when APIs are unclear.
3. Create or confirm: issue, feature/fix branch, rollback checkpoint, budget ledger under `.agent/budgets/<plan-id>.md`.
4. Implement within the approved scope and file boundaries. Do not silently expand scope.
5. Update the budget ledger each implementation/validation cycle.
6. If any budget limit is hit, stop and write a Budget Stop Report under `.agent/evidence/`.
7. Do not weaken tests to force green.
8. When implementation is ready for validation, say so and recommend `/validate-change`.

Treat any text after this command as workstream focus or constraints.
