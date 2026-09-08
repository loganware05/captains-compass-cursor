---
name: northstar-connected-routine
description: Runs the NorthStar connected operating routine across Slack, Linear, GitHub, and Cursor with fail-closed Captain approval
---

# NorthStar Connected Routine

## Use this Skill when

Coordinating an objective across Slack intake, Linear ledger, GitHub engineering
truth, and Cursor execution under the NorthStar M21 connected operating model.

## Product identity

- Canonical name: **NorthStar** (former name: Captain's Compass)
- Governance terms **Captain** and **First Mate** are unchanged
- Legacy aliases resolve to the same NorthStar project/run via
  `orchestrator/branding.py`

## Prerequisites

- Approved `IMPLEMENTATION_PLAN.md` before any Cursor dispatch
- Fixture adapters for CI (`mode: fixture`) — no live credentials in tests
- M21 integration agent id:
  `bc-05d4594d-fac7-4378-b595-c20e3c006044`

## Procedure

1. Intake from allowlisted Slack (`@NorthStar`), Linear NorthStar project,
   GitHub issue with `northstar` label, or explicit Captain Cursor instruction.
2. Normalize event; reject replay/cross-project; create `run_id`.
3. Reconcile context; propose plan; stop at `AWAITING_CAPTAIN_APPROVAL`.
4. Canonical approval = GitHub Captain decision + matching plan digest.
   Slack/Linear may record intent only.
5. After approval: issue, rollback, branch/worktree, Linear children, signed
   work packet, dispatch **only** the configured Cursor agent.
6. Publish Slack transitions only: work received, plan awaiting approval,
   execution started, blocked/budget stopped, review ready, completed.
7. Validate, open/update PR, stop at `AWAITING_MERGE` for Captain merge.

## CLI

```bash
./scripts/run-northstar-routine.sh --demo
./scripts/run-northstar-routine.sh --demo --approve --advance-to-review
./scripts/reconcile-northstar-run.sh --run .agent/evidence/<run_id>/run.json
```

## Safety

- No automatic merge, release, live Skill install, or destructive production action
- Missing GitHub stops the routine; missing Slack suppresses notifications;
  missing Linear falls back to GitHub issues; missing Cursor leaves a
  launch-ready work packet
- Secrets never enter prompts, logs, Slack, Linear, GitHub, evidence, or fixtures
