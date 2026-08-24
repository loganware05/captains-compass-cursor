---
name: persistent-role-promotion
description: Proposes persistent specialist agent roles from proficiency evidence (staging + PR only)
---

# Persistent Role Promotion

## Use this Skill when

A subagent has Captain-approved proficiency at `proficient` or `expert` with
enough Experience evidence, and the Captain wants a **persistent specialist
role** draft prepared for a PR into `.cursor/agents/`.

## Inputs

- Agent id with proficiency under `.agent/agents/proficiency/`
- Optional notes

## Procedure

1. Confirm proficiency gates (Captain-approved, level ≥ proficient, ≥1 Experience id).
2. Propose staging drafts only:

   ```bash
   ./scripts/propose-persistent-role.sh --agent-id compass-evaluator
   ```

3. Review proposal under `.agent/agents/promotions/proposals/` and drafts under
   `.agent/agents/promotions/staging/<agent-id>/`.
4. Open a Captain-reviewed PR to copy drafts into `.cursor/agents/` and
   `orchestrator/reference-profiles/`. Never auto-merge.
5. After merge, optionally record the role in
   `.agent/agents/promotions/registry.json` so the assembler can prefer it.

## Output

- Promotion proposal JSON
- Staging `agent.md` + `reference-profile.json`

## Prohibited actions

- Writing directly to `.cursor/agents/` from this Skill
- Auto-merging persistent-role PRs
- Treating staging drafts as live agents
