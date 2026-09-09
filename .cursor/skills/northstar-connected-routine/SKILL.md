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
- Fixture adapters for CI (`mode: fixtures`) — no live credentials in tests
- Live mode (`--mode live`) requires env secrets + sandbox product allowlist
- M21 integration agent id:
  `bc-05d4594d-fac7-4378-b595-c20e3c006044`

## Procedure

1. Intake from allowlisted Slack (`@NorthStar`), Linear NorthStar project,
   GitHub issue with `northstar` label, GitHub webhook ingress, or explicit
   Captain Cursor instruction.
2. Normalize event; reject replay/cross-project; create `run_id`.
3. Reconcile context; propose plan; stop at `AWAITING_CAPTAIN_APPROVAL`.
4. Canonical approval = GitHub Captain decision + matching plan digest
   (`NORTHSTAR_APPROVE plan_digest=<64-hex>`). Slack/Linear may record intent only.
   Live mode refuses the CLI `--approve` shortcut.
5. After approval: issue, rollback, branch/worktree, Linear children, signed
   work packet, dispatch **only** the configured Cursor agent to the **sandbox**
   product allowlist.
6. Publish Slack transitions only: work received, plan awaiting approval,
   execution started, blocked/budget stopped, review ready, completed.
7. Validate, open/update PR, stop at `AWAITING_MERGE` for Captain merge.

## CLI

```bash
./scripts/run-northstar-routine.sh --demo
./scripts/run-northstar-routine.sh --demo --approve --advance-to-review
./scripts/run-northstar-routine.sh --mode live --product-repo loganware05/captain-compass-sandbox \
  --provider github --event path/to/event.json
./scripts/serve-northstar-ingress.sh --mode live --bind 127.0.0.1 --port 8787
./scripts/run-northstar-routine.sh --demo --approve --advance-to-review \
  --propose-roles --surface-routing --notion-mode fixtures
./scripts/reconcile-northstar-run.sh --run .agent/evidence/<run_id>/run.json
```

See `docs/integrations/northstar-live-ops.md` for env vars and fail-closed rules.

After `REVIEW_READY`, `--propose-roles` stages persistent-role drafts only
(Captain PR required). `--surface-routing` lists pending routing proposals and
does **not** apply weights. Use `./scripts/apply-routing-proposal.sh` with
`captain_approved` for bounded apply. `--notion-mode fixtures|live` gathers
non-authoritative research context / summary mirrors.

## Safety

- No automatic merge, release, live Skill install, or destructive production action
- Missing GitHub stops the routine; missing Slack suppresses notifications;
  missing Linear falls back to GitHub issues; missing Cursor leaves a
  launch-ready work packet
- Secrets never enter prompts, logs, Slack, Linear, GitHub, evidence, or fixtures
- Product dispatch allowlist: `loganware05/captain-compass-sandbox` only
