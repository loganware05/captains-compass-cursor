# Implementation Plan — M55 Captain Handbook + Skills Library Fill (A1)

- Status: APPROVED

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m55-captain-handbook-skills-a1` |
| Linear | [OVA-71](https://linear.app/ovaltechnologysolutions/issue/OVA-71/m55-captain-handbook-skills-library-fill-a1) · [P-OVA-3](https://linear.app/ovaltechnologysolutions/project/northstar-skills-learning-loop-476ac0164351) |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.59.0** @ `c2db26b` |
| Branch | `feature/OVA-71-m55-captain-handbook-skills-a1` |
| Rollback | `rollback/pre-m55-captain-handbook-skills-a1` @ `c2db26b` |
| Captain | Logan Ware |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| When | 2026-10-11 — explicit “approve M55, star REA as well” |
| Notes | REA (`morluto/rea`) starred for **metadata-only** TI candidacy — not an execution/MCP install target |

## Request

Enable the Captain to (1) use NorthStar effectively via one handbook, and (2) feed **starred** GitHub repositories through the Skills Learning Loop so curated Skills carry across product repos via `install.sh` / `update.sh`.

## Current behavior

- Stars → TI → learn → scorecard → promote → PR → install/update is **shipped** (M19–M24, C1/C2).
- Operator seeds exist (`docs/guides/starred-repos-to-skills.md`, `docs/INDEX.md`, onboarding) but no single Captain handbook.
- Library fill (roadmap A1: 3–5 retained Skills with Experience) is incomplete.
- Learning CLIs never clone, install, or execute external repos (ADR-040 / M23).

## Desired behavior

1. **Captain Handbook** at `docs/guides/captain-handbook.md` (linked from `docs/INDEX.md` and README start-here).
2. **A1 library-fill operator package** with selection criteria, fixture dry-run evidence, live Stars checklist; REA noted as starred metadata-only candidate.
3. Light doc hygiene (INDEX, Stars guide, README version pointer). No authority-model changes.

## Out of scope

- Installing or running REA / Hopper / Ghidra / IDA / reverse-engineering MCP inside NorthStar
- Cloning or executing starred repos from the Learning Loop
- Auto-promote / auto-install into `.cursor/skills/`
- Non-starred arbitrary URL ingest
- A2 Linear ledger automation (follow-on)
- AHF-P07, scheduled Overseer GHA

## Open questions (resolved)

1. A1 categories: prefer mix of `devtool`, `backend-library`, `frontend-ui` (Captain may adjust per run).
2. REA: **starred**; **not** an A1 execution target — metadata/procedure Skill draft only if scorecards pass later.

## Workstreams

| ID | Scope |
|---|---|
| W1 | Captain Handbook + INDEX/README links |
| W2 | A1 runbook + fixture evidence under `.agent/evidence/m55-captain-handbook-skills-a1/` |
| W3 | Live Stars checklist (Captain-supervised; REA eligible for TI only) |

## Acceptance criteria

- [x] `docs/guides/captain-handbook.md` exists and is linked from `docs/INDEX.md`
- [x] Handbook states topology, surfaces, Stars→Skill path, portability, and hard non-goals
- [x] A1 runbook + evidence path documented; fixture dry-run recorded
- [x] Doctor + relevant tests pass (`test_m19_skill_learning_loop` OK)
- [x] No auto-promotion; no clone/exec of external repos
- [x] `PROGRESS.md` / `CHANGELOG.md` updated
- [x] Branch + rollback checkpoint (`rollback/pre-m55-captain-handbook-skills-a1`)
- [ ] Live Path B library fill (≥3 Skills) — Captain-supervised follow-on
- [ ] PR opened / merged

## Autonomy budget

| Limit | Value |
|---|---|
| Iterations | 8 |
| Wall time | 4h |
| Scope | Docs + evidence + minimal link hygiene; no Skill auto-install |

## Rollback

- Tag `rollback/pre-m55-captain-handbook-skills-a1` @ `c2db26b`
- Revert PR / delete handbook path
