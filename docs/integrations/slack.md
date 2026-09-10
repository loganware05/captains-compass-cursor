# Slack Integration (NorthStar M21)

Slack is an **intake and notification surface** for NorthStar. It is **not** an
approval authority. Canonical Captain approval remains on GitHub with a matching
plan digest.

## Setup

1. Allowlist one Slack channel for NorthStar intake.
2. Require an explicit `@NorthStar` mention on objectives.
3. Optionally accept legacy `@CaptainCompass` mentions and normalize them to the
   same NorthStar project identity via `orchestrator/branding.py`.
4. Configure Captain user IDs for approval-*intent* verification only.

## Agent behavior

- Normalize inbound events with `SlackAdapter.normalize_event`.
- Publish only allowlisted transitions:
  - work received
  - plan awaiting approval
  - execution started
  - blocked or budget stopped
  - review ready
  - completed
- Thread all notifications to the originating Slack thread.
- Record Slack approval intent with `record_approval_intent` — never dispatch
  Cursor from Slack alone.

## Fallback

If Slack is unavailable, suppress conversation notifications. GitHub and Linear
status updates continue.

## Skill

See `.cursor/skills/northstar-connected-routine/SKILL.md`.

## CLI (fixture mode)

```bash
./scripts/run-northstar-routine.sh --demo
./scripts/run-northstar-routine.sh --event tests/fixtures/northstar/slack-objective.json --provider slack
```

## Live notify (M22)

After GitHub + Linear health, Slack may notify allowlisted transitions in live
mode via `NORTHSTAR_SLACK_BOT_TOKEN`. Slack remains non-authoritative. See
`docs/integrations/northstar-live-ops.md`.
