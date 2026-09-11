# Progress

## Current status

**M24 IMPLEMENTATION IN PROGRESS** — Linear Skills Learning Loop flight recorder
(H0–H3 + M0 + minimal sync → v1.29.0).

| Item | Value |
|---|---|
| Plan | `IMPLEMENTATION_PLAN.md` — **APPROVED** |
| Plan ID | `m24-linear-skills-ledger` |
| Prior release | **v1.28.0** (M23 TI scorecard + skill flywheel) |
| Target release | **v1.29.0** (unreleased / in progress) |
| Plan branch | `cursor/m24-linear-skills-ledger-05fd` |
| Capability artifacts | `.agent/plans/m24-linear-skills-ledger/` |
| Linear project | **NorthStar Skills Learning Loop** (`c62f65bf-a376-4716-b958-0d874730a391`) |
| Linear M0 | **Done by Captain** (project, M0–M7, contracts, Run 001) |
| Working issues | **OVA-6 … OVA-12** (stop before **OVA-13** Captain Gate) |
| Captain guide | `docs/guides/starred-repos-to-skills.md` |

## Completed

- v1.5.0–v1.28.0 / M1–M23 + #50 M4 bridge
- M22: unattended live ops + ingress (v1.27.0)
- M23: `design-system` category, starred provenance, draft evidence gates,
  scorecard path, skill/docs, ADR-040, VERSION 1.28.0
- Sandbox craft-tokens UI experiment + a11y vitest evidence
- Doctor + `./tests/run.sh` **121/121** on release closeout
- Tags/releases: `v1.27.0` (retroactive), `v1.28.0`
- M24 discovery + plan APPROVED (Captain)
- Linear M0 bootstrap completed by Captain (project, milestones, Ledger Contract,
  Agent Routing Contract, Run 001 parent OVA-5 + children OVA-6…OVA-18)
- Control H2/H3 scaffolding present: `scripts/northstar`,
  `scripts/sync-skill-learning-ledger.sh`, `orchestrator/integrations/skills_ledger.py`

## In progress

1. H1 topology runbooks (Skills + Stars guide + Linear docs)
2. Doctor + unit tests for ledger/launcher
3. ADR-041 + CHANGELOG/VERSION/PROGRESS closeout for v1.29.0 slice
4. Linear working path OVA-6…OVA-12 only — **do not** advance OVA-13

## Next

1. Finish validation (`doctor.sh`, `./tests/run.sh`) + evidence pack
2. Adversarial review + PR prep for v1.29.0
3. Stop before OVA-13 (human Captain Gate)

## Blockers

None for the approved H0–H3+M0+minimal-sync slice. Captain Gate (OVA-13) is
intentionally out of agent scope for this pass.
