# M43 Holdout Gate — Jev Ranking Enablement

Plan ID: `m43-jev-ranking-enablement`  
Release: **v1.43.0** (code ships **default-off**)  
Linear: OVA-55

## Purpose

Operational gate for Captain-local live apply (`COMPASS_DECISION_APPLY=1`).
CI green does **not** require live Jev or this holdout.

## Primary metric

**Wrong / unnecessary skill-load rate** — fraction of resolve runs where the
loaded skill set includes a skill that a labeled reviewer marks as wrong or
unnecessary for the objective (relative to the matcher holdout arm).

Secondary (optional ops): matched-skill → task-completion rate when execution
telemetry is available.

## Arms

| Arm | Config |
|---|---|
| Holdout (control) | `COMPASS_DECISION_APPLY` unset — matcher rankings only |
| Treatment | `COMPASS_DECISION_PROVIDER=jev` + `COMPASS_DECISION_APPLY=1` (+ implied shadow) |

Both arms use pinned `COMPASS_JEV_MODEL_ID=jev-1.13.0` when the treatment arm
calls Jev. Hermetic file-provider rehearsal may precede live Jev.

## Tolerance

If treatment shows **>5% relative regression** on the primary metric vs holdout,
**roll back** (unset `COMPASS_DECISION_APPLY` immediately; optionally revert the
M43 tag to `rollback/pre-m43-jev-ranking-enablement`).

Example: holdout wrong-load rate 10%, treatment 10.6% → 6% relative → rollback.

## Invariants (must hold regardless of metric)

1. Applied IDs ⊆ matcher-eligible roster (no eligibility bypass).
2. Abstain / error / gate miss → matcher unchanged.
3. Evidence under `.agent/evidence/m43-jev-ranking-enablement/` only; plans
   store path/ID refs.
4. Thresholds tunable via `COMPASS_DECISION_NOUL_MIN` / `COMPASS_DECISION_CONF_MIN`
   without a code change.

## Rollback procedure

1. Unset `COMPASS_DECISION_APPLY` in the target environment (instant).
2. Confirm resolve rankings match matcher-only baseline.
3. If code rollback needed: check out / deploy
   `rollback/pre-m43-jev-ranking-enablement`.
4. Record outcome under this evidence directory.

## Evidence layout

```text
.agent/evidence/m43-jev-ranking-enablement/
  HOLDOUT_GATE.md          # this file
  VALIDATION.md            # hermetic validation notes
  shadow/<run-id>/         # paired apply/shadow JSON
  holdout/                 # Captain-local labeled results (optional)
```
