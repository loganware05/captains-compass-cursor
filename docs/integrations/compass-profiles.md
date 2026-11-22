# COMPASS_PROFILE v0 (additive gate bundles)

Thin named bundles that set known `COMPASS_*` gates when those keys are
**unset or empty**. Individual flags always win. Profiles never enable live
dual-gates (`COMPASS_SENTRY_LIVE`, etc.).

## Profiles

| Name | Gates set (when unset) |
|---|---|
| `core` | `COMPASS_STATUS_ENABLED`, `COMPASS_BRAIN_ENABLED` |
| `integrations` | `COMPASS_SENTRY_INGEST_ENABLED`, `COMPASS_T3_EXEC_ENABLED`, `COMPASS_APIFY_ENABLED`, `COMPASS_EXPLAIN_ENABLED`, `COMPASS_IDENTITY_ENABLED`, `COMPASS_I6_VALIDATE_ENABLED`, `COMPASS_CONVERSATION_INGEST_ENABLED` |

## Usage

```bash
# Auto-apply on every northstar invocation:
COMPASS_PROFILE=integrations ./scripts/northstar sentry list

# Inspect / export (eval-safe; only emits unset keys):
./scripts/northstar profile list
./scripts/northstar profile show integrations
eval "$(./scripts/northstar profile export core)"
```

## Authority

Profiles do **not** grant Captain approval, auto-merge, or live network access.
Live integrations still require their explicit dual gates + credentials.
