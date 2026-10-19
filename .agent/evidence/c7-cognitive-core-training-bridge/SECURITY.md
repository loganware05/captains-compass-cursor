# Security — c7-cognitive-core-training-bridge

## Threat model (bounded)

| Risk | Mitigation |
|---|---|
| Accidental training / weight mutation | No training code path; schemas lock `auto_uploaded: false` |
| Secret leakage in export | `redact_text` on objective/lessons; checklist `secrets_redacted_ack` required |
| Unauthorized Specialized Model ingest | Review packet requires operator attestations (eval/security/Captain flags); not cryptographic proof — Specialized Model must still verify |
| Authority expansion | `approved_for_execution` / `authority_mutation` const false |
| Silent remote upload | Local `.agent/training-exports/` only; no network clients |
| Confusion with Skill promotion | Cites `from_experience.py` as documented; does not call it |

## Fail-closed

Unset `COMPASS_TRAIN_BRIDGE_ENABLED` → CLI exit 2.
Incomplete export checklist → `TrainBridgeServiceError`.
Silent fixture fallback denied unless `--fixture` / `COMPASS_TRAIN_BRIDGE_FIXTURE=1`.
Default eligibility requires `provenance.reviewed|captain_approved|export_eligible`
(or cycle review markers); `--include-unreviewed` is an explicit override.
