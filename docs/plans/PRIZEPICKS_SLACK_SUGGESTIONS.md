# PrizePicks Slack Suggestions Pipeline

> **APPROVED** 2026-11-26 — plan ID `prizepicks-slack-suggestions`.
> Control issue [#318](https://github.com/loganware05/captains-compass-cursor/issues/318).
> Product issue [PrizePicksBot#4](https://github.com/loganware05/PrizePicksBot/issues/4).
> Rollback: `rollback/pre-prizepicks-slack-suggestions` @ `08c897f`.

Research-only Flex suggestion **compact cards** to Captain Slack **DM** via Bot + OAuth.
Cadence: on-demand CLI + T3 `schedule_task` at **17:00 America/Chicago**.
Feedback: reactions (✅⏭🏆❌) + replies, polled on next run (no Events API in v1).
Live PrizePicks entry remains DENIED.

Product checkout: `/Users/loganware/Documents/Personal/Code/PrizePicksBot-slack-suggestions`
Control checkout: `/Users/loganware/Documents/Personal/Code/captains-compass-prizepicks-slack`
