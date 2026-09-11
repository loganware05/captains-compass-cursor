# M24 closeout evidence — v1.29.0

| Field | Value |
|---|---|
| Plan | `m24-linear-skills-ledger` (APPROVED) |
| Control PR | https://github.com/loganware05/captains-compass-cursor/pull/132 (merged) |
| Control merge | `8065f91da307e03eba86aeff71900fc21661c2b6` on `main` |
| VERSION | `1.29.0` |
| Validation date (UTC) | `2026-09-11` |
| First Mate run | `bc-0b8ec108-10ec-4204-a4e4-8bedbf0405fd` |

## Validation

| Check | Result |
|---|---|
| `./scripts/doctor.sh` | Pass (0 errors) |
| `./tests/run.sh` | **121 passed**, 0 failed |
| Linear project | NorthStar Skills Learning Loop (`c62f65bf-a376-4716-b958-0d874730a391`) |
| Run 001 | `NS-SKILL-001` / OVA-5…OVA-18 — **closed retained** |

## End-to-end learning loop proof (sandbox)

| Item | Value |
|---|---|
| Sandbox Skill | `craft-tokens-design-system` (`AVAILABLE_SKILL`, retained) |
| Sandbox PR | https://github.com/loganware05/captain-compass-sandbox/pull/46 (**merged**) |
| Merge commit | `3928e7beecb0678a2e110102ae2a1d3d10f6cd18` |
| Captain retain | OVA-18 / `.agent/learning-runs/NS-SKILL-001/14-lifecycle-decision.md` |
| `approved_for_execution` | **false** (held) |

## Deferred (not in v1.29.0)

- Router live wakeability re-check before `availability=1.0` for expired agent pins
  (learning from OVA-17 Experience; optional follow-up)

## Authority note

Linear records only. Repository / GitHub evidence is canonical.
