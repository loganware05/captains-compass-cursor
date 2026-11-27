# Progress

## Current status

**IN PROGRESS:** [#318](https://github.com/loganware05/captains-compass-cursor/issues/318) —
`prizepicks-slack-suggestions` on `feature/318-prizepicks-slack-suggestions` → **v1.96.0**.

| Item | Value |
|---|---|
| Baseline | **v1.95.0** @ `08c897f` |
| Plan | `prizepicks-slack-suggestions` **APPROVED** |
| Issue | [#318](https://github.com/loganware05/captains-compass-cursor/issues/318) |
| Product | PrizePicksBot [#4](https://github.com/loganware05/PrizePicksBot/issues/4) |
| Rollback | `rollback/pre-prizepicks-slack-suggestions` @ `08c897f` |

Product worktree implements Slack CLI; control ships orchestration docs/procedure.

## Standing order

Approve ⇒ implement → validate → commit → open PR. Merge remains Captain-only.

## Next

1. Open dual PRs; live Slack smoke after Captain secrets
2. Create T3 `schedule_task` at 17:00 America/Chicago

## Blockers

- Live Slack bot token + Captain user ID not yet provided
