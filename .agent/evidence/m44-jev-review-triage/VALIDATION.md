# M44 Validation — Review Triage Shadow

## Hermetic

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -B -m unittest \
  tests.orchestrator.test_m41_decision_provider \
  tests.orchestrator.test_m43_decision_apply \
  tests.orchestrator.test_m44_review_triage -v
```

Defaults: `COMPASS_DECISION_REVIEW_SHADOW` unset → review pipeline unchanged; no network.

## File-provider shadow smoke

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_REVIEW_SHADOW=1 \
./scripts/run-code-review.sh --repo-root . --base HEAD~1
```

Expect evidence under `.agent/evidence/m44-jev-review-triage/shadow/` with
`applied: false` and findings identical to baseline.

## Rollback

Unset `COMPASS_DECISION_REVIEW_SHADOW`. Tag: `rollback/pre-m44-jev-review-triage`.
