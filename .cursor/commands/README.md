# Cursor commands (Captain's Compass)

Project slash commands live in this directory as plain Markdown files.
In Cursor Agent chat, type `/` and select a command. Text after the command
name is passed through as additional context.

| Command | Phase |
|---|---|
| `/initialize-project` | Onboard / fill project context (no product implementation) |
| `/plan-feature` | Write `IMPLEMENTATION_PLAN.md` → AWAITING APPROVAL; stop |
| `/implement-approved-plan` | Implement only if plan is APPROVED |
| `/validate-change` | Run validation + collect evidence per evidence matrix |
| `/prepare-pr` | Open or draft PR with evidence |
| `/close-workstream` | Mark plan complete; update memory after merge |

Commands are thin wrappers over Compass Skills and rules. They do **not** bypass
the approval gate, fail-closed critical hooks, or autonomy budgets.
