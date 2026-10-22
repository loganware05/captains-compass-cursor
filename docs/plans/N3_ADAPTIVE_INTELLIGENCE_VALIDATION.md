> **DRAFT / FOLLOW-ON** (2026-10-22) — Plan ID `n3-adaptive-intelligence-validation`.
> Prerequisite: **N2** Product Integration Validation complete (or parallel
> bounded evals with Captain approval).
> Not the active root `IMPLEMENTATION_PLAN.md` until Captain promotes it.

# N3 — Adaptive Intelligence Validation

## One-line summary

Connect execution outcomes to learning, routing, and specialized-model
evaluations; measure whether recommendations improve against fixed baselines.

## Suggested scorecard

| Metric | Definition |
|---|---|
| Project-state accuracy | Grounded claims / checked claims |
| Difficulty calibration | Predicted vs observed effort/failures |
| Routing effectiveness | Quality, latency, cost vs baseline |
| Skill reuse | Successful reuse on independent tasks |
| Review precision | Accepted verified findings / decided findings |
| Context efficiency | Relevant evidence retrieved per token |
| Training effectiveness | Held-out performance vs retrieval-only baseline |

All policy/Skill/routing changes remain Captain-gated.

## Non-goals

Silent self-modification; auto-promotion of adapters; Level 3 spend without
Level 0–2 proof-of-value.
