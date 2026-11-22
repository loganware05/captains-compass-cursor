# Evidence — audit-p2-sentry-profiles (#288)

| Field | Value |
|---|---|
| Plan | `audit-p2-sentry-profiles` |
| Issue | #288 |
| Branch | `feature/288-audit-p2-sentry-profiles` |
| Baseline | `bb8f334` / v1.87.2 |
| Rollback | `rollback/pre-audit-p2-sentry-profiles` |
| Release | v1.88.0 |

## Validation

| Check | Result | Artifact |
|---|---|---|
| Unit: window_hours + profiles | pass (12) | (inline unittest) |
| `./scripts/doctor.sh` | pass | `doctor.txt` |
| `./tests/run.sh` | 138 passed, 0 failed | `tests-run.txt` |

## Security notes

- Live Sentry remains dual-gated (`COMPASS_SENTRY_INGEST_ENABLED` + `COMPASS_SENTRY_LIVE`)
- Profiles never set live dual-gates
- RecordingTransport redacts auth headers in window_hours unit test
- No write/mutate Sentry; authority locks unchanged
