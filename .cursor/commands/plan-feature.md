Create or update an approval-gated implementation plan for the Captain's request.

1. Load Skills `implementation-planning` and `capability-planning` and follow them.
2. Read required project memory docs and inspect the current implementation.
3. Run `./scripts/capability-plan.sh --plan-id <plan-id> "<objective>"` and merge the rendered capability sections into root `IMPLEMENTATION_PLAN.md`.
4. Complete remaining human-authored plan sections per `implementation-planning`.
5. Write or update root `IMPLEMENTATION_PLAN.md`.
6. Set status to **AWAITING APPROVAL**.
7. Include Autonomy Budget fields and note the ledger path `.agent/budgets/<plan-id>.md`.
8. Reference `docs/EVIDENCE_MATRIX.md` (or the installed copy) in Testing / Definition of Done.
9. Present the plan to the Captain and **stop**. Do not implement product files.

Treat any text after this command as the feature request / scope hint.
