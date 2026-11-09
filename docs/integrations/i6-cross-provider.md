# I6 cross-provider validation

Hermetic harness that measures I1–I5 gated fixture surfaces and writes a
scorecard. **No live network. No authority grants.**

## Gate

```bash
COMPASS_I6_VALIDATE_ENABLED=1
```

## Command

```bash
COMPASS_I6_VALIDATE_ENABLED=1 ./scripts/northstar validate integrations
```

Optional `--no-write` skips evidence persistence.

## Providers probed

| ID | Surface | Checks |
|---|---|---|
| I1 | Sentry | fail-closed + fixture fetch |
| I2 | T3 | fail-closed + fixture capabilities/start |
| I3 | Apify | fail-closed + fixture search |
| I4 | Scrimba Explain | fail-closed + fixture create |
| I5 | WorkOS identity | fail-closed + fixture sync |

## Evidence

Scorecards land under `.agent/evidence/i6-cross-provider/` with
`approved_for_execution: false` / `authority_mutation: false` /
`auto_promoted: false`.
