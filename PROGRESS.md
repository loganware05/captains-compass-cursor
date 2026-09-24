# Progress

## Current status

**In flight: M41 / v1.42.0** — Jev Decision Service shadow skill suggestion
(Captain-approved 2026-09-24).

| Item | Value |
|---|---|
| Baseline | **v1.41.0** @ `cec4da2` |
| In flight | **M41** — branch `cursor/m41-jev-decision-service-753c` |
| Plan | `IMPLEMENTATION_PLAN.md` — **APPROVED — IMPLEMENTING** (`m41-jev-decision-service`) |
| Rollback | `rollback/pre-m41-jev-decision-service` @ `cec4da2` |
| Evidence | `.agent/evidence/m41-jev-decision-service/` |
| Budget | `.agent/budgets/m41-jev-decision-service.md` |

## In flight

- WS0: `SKILL_SLUGS` includes `code-reviewer` + `northstar-connected-routine`
- WS1–WS5: DecisionProvider stub/file/jev + shadow wiring + tests + ADR-058
- Remaining: full suite validation, adversarial review, PR update, Captain merge

## Completed

- **M40 → v1.41.0** — filesystem-gated context (inodes, routes, boundary gate,
  skill inodes, subagent pwd)
- M39 → v1.40.0 / v1.40.1
- M37 → v1.39.0; Track B through B5 / v1.36.0

## Known follow-ups (deferred)

1. M37 specialist FP on *removed* diff lines (scan added lines only)
2. ~~Compiler `SKILL_SLUGS` gap~~ — **closed in M41 WS0**

## Next trials after M41 shadow (Captain-ordered; separate plans)

1. Ranking enablement
2. Review triage
3. Agent routing

## Blockers

None.
