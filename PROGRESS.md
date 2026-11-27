# Progress

## Current status

**MERGED / COMPLETE:** [#319](https://github.com/loganware05/captains-compass-cursor/pull/319)
for [#318](https://github.com/loganware05/captains-compass-cursor/issues/318)
`prizepicks-slack-suggestions` → **v1.96.0** @ `3e8c985`.

| Item | Value |
|---|---|
| Baseline | **v1.95.0** @ `08c897f` |
| Merge | `3e8c985` |
| Tag | `v1.96.0` |
| Rollback | `rollback/pre-prizepicks-slack-suggestions` @ `08c897f` |
| Product | [PrizePicksBot#5](https://github.com/loganware05/PrizePicksBot/pull/5) / [#4](https://github.com/loganware05/PrizePicksBot/issues/4) **merged** |

### Delivered

- NorthStar/T3 procedure for PrizePicksBot research-only Slack DMs
- Daily schedules **11:00** and **17:00** America/Chicago (bound to Slack suggestions thread)
- Live DM smoke + Captain visual confirm of compact card format
- Product Slack CLI (`slack publish|poll`, reaction/reply ledger)

## Standing order

Approve ⇒ implement → validate → commit → open PR. Merge remains Captain-only.

## Next

Pick the next product plan when ready:

- XRV live-local ops smoke (real tip SHA; no production deploy) if still deferred
- Bend CI var enable (`COMPASS_BEND_STRICT_LAWS_CI=1`) — ops, not code
- Specialized Model Level 3 (#237) — still paused

## Blockers

None.
