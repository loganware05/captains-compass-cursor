# XRV Pilot C — PrizePicksBot Onboard / Baseline

> **COMPLETE** — PrizePicksBot [#3](https://github.com/loganware05/PrizePicksBot/pull/3)
> merged @ `187a695` (2026-11-11). Issue [#2](https://github.com/loganware05/PrizePicksBot/issues/2) closed.
> Control EER: `.agent/evidence/xrv/eer-prizepicks-pilot-c-baseline.json` (`lifecycle_state: merged`).
> Plan ID: `xrv-pilot-c-onboard-baseline`.
> Approved by Captain (`I approve`, 2026-11-11) in T3 Pilot C handoff thread.

## Money-safety (hard)

**DENIED:** live wagers, PrizePicks submit/login/cookie replay, captcha bypass,
`approved_for_execution: true`, real-money API writes.

**ALLOWED:** fixture boards/odds, paper ledger, mocked HTTP, control-repo
product readiness assess.

## Shipped

Board dump schema validation + configurable stale-age gate; fixture-only tests;
CLI flags `--max-board-age-hours`, `--allow-stale-board`, `--require-board-timestamp`.

## Acceptance

- [x] Issue + feature branch + rollback on PrizePicksBot
- [x] Evidence packet + inventory
- [x] Malformed/aged board fixtures fail closed or warn per policy
- [x] `pytest` green; no-submit invariants retained
- [x] Control EER at `merged` after product PR
- [x] Locks remain false

## Deferred

Odds API retries, Compass refresh, transfer-learning, live Odds smoke,
ops-verified / adaptive benefit, any live-money surface.
