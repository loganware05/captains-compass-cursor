# M43 Validation — Ranking Enablement

## Hermetic (CI / doctor)

```bash
./scripts/doctor.sh
python -B -m unittest tests.orchestrator.test_m41_decision_provider \
  tests.orchestrator.test_m43_decision_apply -v
```

Defaults: `COMPASS_DECISION_APPLY` unset → rankings identical to matcher; no network.

## File-provider apply smoke

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_APPLY=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

Expect evidence under `.agent/evidence/m43-jev-ranking-enablement/shadow/` with
`applied: true` when the fixture order differs from matcher and gates pass
(Noul ≥ 0.70, confidence ≥ 0.60).

## Shadow-only regression

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_SHADOW=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

`recommended_skill_ids` must match matcher; evidence under m41 path; `applied: false`.

## Rollback

Unset `COMPASS_DECISION_APPLY`. Optional code tag:
`rollback/pre-m43-jev-ranking-enablement`.
