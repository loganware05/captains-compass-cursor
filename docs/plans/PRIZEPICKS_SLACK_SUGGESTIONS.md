# PrizePicks Slack Suggestions Pipeline

> **COMPLETE** 2026-11-26 — plan ID `prizepicks-slack-suggestions` → **v1.96.0**.
> Control [#318](https://github.com/loganware05/captains-compass-cursor/issues/318) / PR [#319](https://github.com/loganware05/captains-compass-cursor/pull/319) @ `3e8c985`.
> Product [#4](https://github.com/loganware05/PrizePicksBot/issues/4) / PR [#5](https://github.com/loganware05/PrizePicksBot/pull/5) @ `a38f1d1`.
> Rollback: `rollback/pre-prizepicks-slack-suggestions` @ `08c897f`.

Research-only Flex suggestion **compact cards** to Captain Slack **DM** via Bot + OAuth.
Cadence: on-demand CLI + T3 `schedule_task` at **11:00** and **17:00** America/Chicago.
Feedback: reactions (✅⏭🏆❌) + replies, polled on next run (no Events API in v1).
Live PrizePicks entry remains DENIED. Live smoke + Captain visual confirm completed.
