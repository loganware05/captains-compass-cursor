---
name: linear-integration
description: Reads and updates Linear issues/workstream tasks and links them to pull requests when MCP or API access is available
---

# Linear Integration (MCP Stage 3)

## Use this Skill when

Reading Linear issues, creating workstream tasks, updating task statuses, or linking pull requests to Linear work items.

## Prerequisites

- Linear MCP enabled in Cursor **or** Linear API access configured by the Captain
- Do not invent ticket IDs; verify against Linear when connected

## Allowed Stage 3 capabilities

- Reading issues
- Creating workstream tasks
- Updating task statuses
- Linking pull requests

## Procedure

1. Confirm Linear access (MCP tool list or documented API).
2. Prefer linking the approved IMPLEMENTATION_PLAN.md / GitHub issue to the Linear parent.
3. Create child workstream tasks only when parallel streams are cleanly separable.
4. Update status to reflect plan gate: planned → in progress after approval → done after validation.
5. Link the GitHub PR URL when available; otherwise note the PR-ready description.
6. If Linear is unavailable, fall back to GitHub issues / local placeholders and report the gap.

## Prohibited actions

- Do not auto-close parent epics without Captain confirmation
- Do not store secrets in Linear descriptions
- Do not treat Linear as the only source of truth for approval (repo IMPLEMENTATION_PLAN.md wins)
