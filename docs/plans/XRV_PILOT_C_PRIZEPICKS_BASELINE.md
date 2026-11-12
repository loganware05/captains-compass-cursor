# XRV Pilot C — PrizePicksBot Onboard / Baseline

> **APPROVED (product workstream)** — Captain utterance `I approve` on 2026-11-11
> in T3 thread `XRV Pilot C PrizePicksBot baseline inventory`.
> Plan ID: `xrv-pilot-c-onboard-baseline`.
> Product repo: `https://github.com/loganware05/PrizePicksBot`
> Local checkout: `/Users/loganware/Documents/Personal/Code/PrizePicksBot`
> Control closeout issue: [#268](https://github.com/loganware05/captains-compass-cursor/issues/268).

## Money-safety (hard)

**DENIED:** live wagers, PrizePicks submit/login/cookie replay, captcha bypass,
`approved_for_execution: true`, real-money API writes.

**ALLOWED:** fixture boards/odds, paper ledger, mocked HTTP, control-repo
`northstar assess readiness --profile product` against the local checkout.

## Discovery verdict

PrizePicksBot is a **read-only research CLI** (`flex_friday`) with NorthStar
markers present. No live wager/submit path. First bounded task:

**Board dump schema validation + stale board age gate** (fixture-only tests).

## Acceptance (product PR)

- [ ] Issue + feature branch + rollback on PrizePicksBot
- [ ] Evidence packet + inventory
- [ ] Malformed/aged board fixtures fail closed or warn per policy
- [ ] `pytest` green; no-submit invariants retained
- [ ] Control EER `.agent/evidence/xrv/eer-prizepicks-pilot-c-baseline.json`
      promoted past `planned` after product PR merges
- [ ] Locks remain false

## Non-goals

Odds API retries, Compass refresh 1.22→1.85, transfer-learning, live Odds smoke,
any live-money surface.
