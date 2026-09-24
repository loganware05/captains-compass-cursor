# M41 Validation Evidence — Jev Decision Service (shadow)

## Metadata

| Field | Value |
|---|---|
| Plan ID | `m41-jev-decision-service` |
| Date | 2026-09-24 |
| Branch | `cursor/m41-jev-decision-service-753c` |
| Rollback | `rollback/pre-m41-jev-decision-service` @ `cec4da2` |
| Version | **1.42.0** |

## Acceptance criteria

| # | Criterion | Result |
|---|---|---|
| 1 | Defaults: doctor + tests + evals, zero DecisionProvider network | **PASS** — stub default; suite 125 / evals 43 |
| 2 | file + shadow writes evidence; rankings bit-identical to baseline | **PASS** — `test_shadow_file_does_not_change_recommended_ids` |
| 3 | Stub/unknown never raises into capability-plan | **PASS** — unknown → stub; resolve swallows shadow errors |
| 4 | Jev refuses without pinned `COMPASS_JEV_MODEL_ID` | **PASS** — empty/alias/non-`jev-1.13.0` refused |
| 5 | Compact state redaction invariants | **PASS** — top-level + nested forbidden keys; secret patterns |
| 6 | Docs: shadow ≠ dispatch | **PASS** — `docs/integrations/decision-provider.md` + ADR-058 |
| 7 | Hermetic eval report metrics | **PASS** — `.agent/evidence/m41-jev-decision-service/eval/file-provider-eval-v1.json` |
| 8 | No change to agent router / boundary / plan-approval / promotion | **PASS** — DecisionProvider only on resolve shadow path |
| 9 | Rollback path | **PASS** — tag + unset env restores matcher-only |

## Commands

```bash
./scripts/doctor.sh                          # 0 errors
./tests/run.sh                               # 125 passed
./tests/evals/run.sh                         # 43 passed
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m41_decision_provider -v
COMPASS_DECISION_PROVIDER=file COMPASS_DECISION_SHADOW=1 \
  ./scripts/capability-resolve.sh "Build accessible forms with React"
```

## Eval metrics (file provider, hermetic)

See `eval/file-provider-eval-v1.json`:

- wrong_skill_loads: 0
- unnecessary_skill_loads: 0
- missed_useful_skills: 0
- disagreement_rate vs matcher labels: 0.67 (expected — shadow compare, not enablement)
- latency_ms: 0 / cost_usd: 0

## Adversarial remediation

| ID | Finding | Fix |
|---|---|---|
| B1 | Missing eval report | Added `eval.py` + evidence JSON |
| H1 | Out-of-roster Jev IDs | Filter + abstain `out_of_roster` |
| H2 | Empty model id defaulted | Require explicit `COMPASS_JEV_MODEL_ID` |
| M1 | Weak alias refusal | Allowlist exact `jev-1.13.0` |
| M2 | Nested forbidden keys | Recursive `assert_state_safe` |
| L1 | Stale compiler comment | Updated |
| L3 | Evidence noise in tests | Cleanup after integration test |

## Security notes

- No API keys written to evidence env block (model id name only)
- Live Jev never CI default
- Suggestions never set `approved_for_execution`

## Rollback

```bash
git checkout rollback/pre-m41-jev-decision-service
# or unset COMPASS_DECISION_PROVIDER / COMPASS_DECISION_SHADOW
```
