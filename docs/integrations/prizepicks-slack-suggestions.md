# PrizePicks Slack Suggestions (NorthStar experience)

Orchestrates **PrizePicksBot** research-only Flex suggestion DMs. Slack is a
delivery surface — **not** a NorthStar approval authority and **not** a
PrizePicks submitter.

## Ownership

| Layer | Repo | Responsibility |
|---|---|---|
| Product | `loganware05/PrizePicksBot` | Rank → compact card → Slack DM; poll feedback ledger |
| Experience | `loganware05/captains-compass-cursor` | Procedure + T3 `schedule_task` ritual |
| Secrets | Captain | `PRIZEPICKS_SLACK_BOT_TOKEN`, `PRIZEPICKS_SLACK_CAPTAIN_USER_ID` |

Do **not** reuse `NORTHSTAR_SLACK_BOT_TOKEN` for picks unless Captain consolidates apps later.

## On-demand

```bash
cd /path/to/PrizePicksBot
export PRIZEPICKS_SLACK_BOT_TOKEN=...
export PRIZEPICKS_SLACK_CAPTAIN_USER_ID=...

python -m flex_friday slack publish \
  --board path/to/board.json \
  --odds path/to/odds.json \
  --mode daily \
  --poll-prior
```

Dry-run without secrets:

```bash
python -m flex_friday slack publish --board ... --odds ... --mode daily --dry-run
```

## Daily schedule (T3)

Create/update with MCP `schedule_task`:

- **Title:** PrizePicks daily Flex Slack DM
- **Schedule:** `fixed_time`, `timeOfDay` = `23:00` UTC while America/Chicago is **CST**
  (UTC−6); use `22:00` UTC during **CDT** (UTC−5). Re-check at DST boundaries.
- **Local intent:** 17:00 America/Chicago every day (default; Captain may narrow weekdays)
- **Prompt (sketch):**

```text
Run PrizePicksBot research-only Slack suggestion ritual:
1) In PrizePicksBot checkout, poll prior card if ledger exists.
2) Rank daily Flex from current board/odds (allow-stale only if Captain noted).
3) Publish compact DM via `python -m flex_friday slack publish ... --poll-prior`.
4) Confirm channel+ts in reply; never place PrizePicks entries.
5) If board missing/stale, post/fail closed with a blocked notice — do not invent picks.
```

Bind to the Slack suggestions thread or a dedicated ops thread (`bindToCurrentThread`
per Captain preference).

## Feedback loop

On each run, PrizePicksBot polls the prior DM:

| Reaction | Meaning |
|---|---|
| ✅ | entered |
| ⏭ | skipped |
| 🏆 | won |
| ❌ | lost |

Reply keywords: `entered` / `skipped` / `won` / `lost` / `boost` / `guarantee` /
`taco` / `flash`. Stored under PrizePicksBot `data/slack_suggestions/ledger.json`.

## Authority boundaries

- Canonical plan approval remains GitHub + plan digest (NorthStar).
- Slack reactions never approve control-repo plans.
- PrizePicks Terms §8.2: no auto-entry.

## Related

- Plan ID `prizepicks-slack-suggestions`
- Skill notes: `northstar-connected-routine` (Slack non-authoritative)
- Product README Slack section
