# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m9-skill-promotion-artifacts
- Issue: [#70](https://github.com/loganware05/captains-compass-cursor/issues/70) — M9: Skill promotion lifecycle + Artifact Context (v1.13.0)
- Branch: `feature/70-m9-skill-promotion-artifacts` (merged #71)
- Target release: **v1.13.0** (released 2026-08-24)
- Created: 2026-08-24
- Last updated: 2026-08-24
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: v1.13.0; Artifact Context included; --captain-approved for APPROVED+; PROVEN_SKILL ≥2 successful Experiences; dedicated skill-lifecycle Skill
- Rollback checkpoint: `rollback/pre-m9-skill-promotion-artifacts` @ `d2ec205`
- Feature PR: [#71](https://github.com/loganware05/captains-compass-cursor/pull/71) (merged @ `e451554`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1–M8 COMPLETE (v1.5.0–v1.12.0)
  - Baseline: **v1.12.0** (`d2ec205` / current `main` after closeout #69)
- Machine artifacts: `.agent/plans/m9-skill-promotion-artifacts/`

## Request

Proceed with **Milestone 9** of the Captain Compass multi-agent orchestration OS:

1. **Skill promotion lifecycle completion** — raise the Captain-gated candidate ceiling
   past `SANDBOX_TESTED` through `APPROVED` → `AVAILABLE_SKILL` → `PROVEN_SKILL`
   (staging + proposals only; never auto-install or set `approved_for_execution: true`).
2. **Artifact Context** — surface `kind: artifact` knowledge in capability plans
   (always rendered; empty when none).
3. **Dedicated `skill-lifecycle` Skill** — promotion + proficiency training path.

## Problem Statement

After M8:

- Notion §9 item 9 (*Skill promotion lifecycle*) is only half-shipped:
  ceiling hard-coded at `SANDBOX_TESTED`
- No formal Captain-flagged path to `APPROVED` / `AVAILABLE_SKILL` proposals /
  `PROVEN_SKILL` from Experience evidence
- Plan writer lacks **Artifact Context** for the fifth Notion knowledge form

## Desired Outcome

After M9 (v1.13.0):

1. Advance to `APPROVED` / `AVAILABLE_SKILL` / `PROVEN_SKILL` with `--captain-approved`
2. `AVAILABLE_SKILL` writes install **proposals** only (never live Skills)
3. `PROVEN_SKILL` requires ≥2 successful Experiences referencing the skill slug
4. **Artifact Context** always rendered in plans
5. New Skill `skill-lifecycle` (35 Skills)

## Acceptance Criteria

- [x] Extend stages through `PROVEN_SKILL` with evidence + `--captain-approved` for APPROVED+
- [x] `promote-candidate.sh` supports new stages; rejects missing Captain flag / evidence
- [x] `AVAILABLE_SKILL` writes proposal under
      `.agent/capabilities/candidates/available-proposals/<slug>/`
- [x] `PROVEN_SKILL` requires ≥2 successful Experiences (default)
- [x] Plan writer **Artifact Context** (always rendered; empty when none)
- [x] New Skill `skill-lifecycle`; extend `candidate-promotion` docs; ADR-025
- [x] Doctor / tests / evals pass (35 Skills)
- [ ] Control-repo only; sandbox refresh after release (closeout PR)

## Non-Goals

- Auto-install Skills into `.cursor/skills/` or auto-merge promotion PRs
- Setting `approved_for_execution: true`
- Mutating matcher weights from promotion or Artifact Context
- Production embedding / vector DB providers
- Notion MCP / NotebookLM knowledge ingestion (defer M10+)
- Broader live TI providers
- TTL background TI cache refresh

## Open Questions (Captain — resolved 2026-08-24)

1. **Target version:** **v1.13.0**
2. **Artifact Context:** **included** in M9
3. **`APPROVED` gate:** require **`--captain-approved`** for APPROVED+
4. **`PROVEN_SKILL` threshold:** **≥2** successful Experiences
5. **Skills:** new dedicated **`skill-lifecycle`** Skill

## Workstreams / Tasks

| ID | Workstream | Depends | Parallel? |
|---|---|---|---|
| T-A | Promotion stage model + gates + tests | — | no |
| T-B | AVAILABLE / PROVEN proposal writers + CLI | T-A | no |
| T-C | Artifact Context in plan writer + fixtures | — | yes w/ T-A |
| T-D | skill-lifecycle Skill, doctor, ADR-025, docs | T-B, T-C | no |
| T-E | Validation evidence + feature PR | T-D | no |
| T-F | Release prep v1.13.0 | T-E | no |

## Approval Boundary

**Implementation may begin — Captain approved 2026-08-24.**

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-24
- **Approved revision:** v1.13.0; Artifact Context; --captain-approved for APPROVED+; PROVEN ≥2 Experiences; skill-lifecycle Skill
- **Issue:** #70
- **Branch:** feature/70-m9-skill-promotion-artifacts
- **Rollback:** rollback/pre-m9-skill-promotion-artifacts @ d2ec205
- **Feature PR:** #71 (merged)
- **Release:** v1.13.0 (2026-08-24)
