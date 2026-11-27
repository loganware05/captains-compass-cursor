# Implementation Plan — PrizePicks Slack Suggestions Pipeline

- Status: **APPROVED / IMPLEMENTING**

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain |
| Approved at | 2026-11-26 |
| Issue | [#318](https://github.com/loganware05/captains-compass-cursor/issues/318) |
| Product issue | PrizePicksBot [#4](https://github.com/loganware05/PrizePicksBot/issues/4) |
| Rollback | `rollback/pre-prizepicks-slack-suggestions` @ `08c897f` |
| Branch (control) | `feature/318-prizepicks-slack-suggestions` |
| Branch (product) | `feature/4-slack-suggestions-dm` |
| Worktree (control) | `/Users/loganware/Documents/Personal/Code/captains-compass-prizepicks-slack` |
| Worktree (product) | `/Users/loganware/Documents/Personal/Code/PrizePicksBot-slack-suggestions` |

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `prizepicks-slack-suggestions` |
| Budget | `.agent/budgets/prizepicks-slack-suggestions.md` |
| Durable copy | `docs/plans/PRIZEPICKS_SLACK_SUGGESTIONS.md` |

## Goal

NorthStar/T3 orchestrates PrizePicksBot research-only Slack DM suggestion cards:
on-demand + daily **17:00 America/Chicago**. Product owns Slack client; control owns
experience procedure + schedule ritual.

## Acceptance (control)

- [x] Approved plan + issues + worktrees
- [ ] Procedure doc for T3 schedule + on-demand
- [ ] Docs/memory updated
- [ ] PR opened; product PR linked

Full product acceptance tracked on PrizePicksBot #4.
