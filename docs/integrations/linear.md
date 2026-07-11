# Linear Integration (Stage 3)

## Enable (Cursor MCP)

Enable Linear MCP with permissions limited to:

- Reading issues
- Creating workstream tasks
- Updating task statuses
- Linking pull requests

## Agent behavior

Use Skill `.cursor/skills/linear-integration/SKILL.md`.

When Linear is connected, the First Mate may create/update workstream tasks after plan approval and link the GitHub PR.

When unavailable, use GitHub issues or `local/<slug>` placeholders (same fallback pattern as GitHub Stage 1).

## Authority

`IMPLEMENTATION_PLAN.md` in the product repository remains the approval gate. Linear tracks work; it does not replace Captain approval.
