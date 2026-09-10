# Linear Integration (Stage 3 / NorthStar ledger)

## Enable (Cursor MCP)

Enable Linear MCP with permissions limited to:

- Reading issues
- Creating workstream tasks
- Updating task statuses
- Linking pull requests

## Agent behavior

Use Skill `.cursor/skills/linear-integration/SKILL.md` and, for the connected
routine, `.cursor/skills/northstar-connected-routine/SKILL.md`.

When Linear is connected, the First Mate may create/update NorthStar parent
initiative and child workstream tasks after plan approval and link the GitHub PR.

When unavailable, use GitHub issues or `local/<slug>` placeholders (same fallback pattern as GitHub Stage 1).

## Authority

`IMPLEMENTATION_PLAN.md` in the product repository remains the approval gate.
Linear is a **work ledger** for NorthStar — it tracks workstreams and does not
replace Captain approval or GitHub engineering truth.

## Live ledger (M22)

Live Linear create/update/link runs over the injectable transport when
`--mode live`. Linear still cannot approve or dispatch. See
`docs/integrations/northstar-live-ops.md`.
