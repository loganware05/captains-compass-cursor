# Implementation Plan — Autonomous Skill Learning Loop (M19 / M20)

- Status: **APPROVED**
- Plan ID: `m19-autonomous-skill-learning`
- Issue: [#111](https://github.com/loganware05/captains-compass-cursor/issues/111)
- Baseline: v1.22.0 (`3c4455e` on `main`)
- Rollback: `rollback/pre-m19-skill-learning`
- Branch: `feature/111-m19-skill-learning-loop`

| Field | Value |
|---|---|
| **Plan ID** | `m19-autonomous-skill-learning` |
| **Status** | **APPROVED** |
| **Baseline** | v1.22.0 (`3c4455e`) |
| **Issue** | [#111](https://github.com/loganware05/captains-compass-cursor/issues/111) |
| **Target release** | **v1.23.0** (M19); M20 → v1.24.0 |
| **Branch** | `feature/111-m19-skill-learning-loop` |
| **Rollback** | `rollback/pre-m19-skill-learning` |
| **Captain approval** | 2026-09-03 |

## Captain decisions (locked 2026-09-03)

| # | Topic | Decision |
|---|---|---|
| 1 | Autonomy | Automate staging + evidence; **Captain approval gate** when promoting a Skill to go live |
| 2 | Roadmap shape | **Split M19 / M20** |
| 3 | Learning target | Draft **new** Skills **and** improve **existing** Skills from categorized stars (when processes are similar) |
| 4 | Sandbox harness | **Fixture harness + interactive checklist** |
| 5 | Default input | **Fixtures** in CI; `ti-cache` / `live` Captain-local |
| 6 | Skill packaging | New Skill **`skill-learning-loop`** — learning loop for new drafts **and** improve existing Skills when processes are similar |

## Problem statement

M13–M18 shipped learning pieces in isolation (Stars categorization, promotion,
Experience training, release smokes) without a closed Captain-gated loop that
uses categorized Stars in the sandbox to stage candidates, test drafts, and
propose Skill improvements.

## Desired behavior (M19)

1. Explicit `./scripts/run-skill-learning-loop.sh` orchestrates (fixtures default):
   - categorize Stars (M14)
   - select top-N candidates by category + objective
   - export staging candidate JSON
   - run fixture sandbox harness → evidence
   - advance to `SANDBOX_TESTED` when evidence passes
   - emit unified drafts **or** improvement proposals for similar existing Skills
   - **stop** — live install requires Captain (`--captain-approved` / PR)
2. New Skill `skill-learning-loop` documents both paths.
3. Automated smoke + behavioral checklist item 9.
4. ADR: automated staging ≠ auto-install.

## Non-goals

- Auto-merge / auto-copy into `.cursor/skills/`
- `approved_for_execution: true`
- Cloning or executing starred repos
- Hook/CI auto-run of the full loop
- Weakening Captain gates for live promotion

---

## Roadmap

| Milestone | Version | Theme | Status |
|---|---|---|---|
| **M19** | v1.23.0 | Learning orchestrator, staging export, fixture harness, unified drafts, similarity improvement **proposals**, Skill `skill-learning-loop` | **PR #112** (ready for review) |
| **M20** | v1.24.0 | Experience bridge → PROVEN path; Captain-gated apply of existing-Skill improvements | **In progress** (#113) |

---

# M19 — Autonomous Skill Learning Loop (v1.23.0)

## Acceptance criteria

1. `./scripts/run-skill-learning-loop.sh --source fixtures` exits 0 with artifacts under `.agent/`.
2. Writes staging candidates, harness evidence, drafts and/or improvement proposals; does **not** write under `.cursor/skills/` (except the new committed Skill itself).
3. Promotion past `SANDBOX_TESTED` still requires `--captain-approved`.
4. `approved_for_execution` remains `false`.
5. Similar existing Skills get improvement proposals (not silent mutation).
6. Unit tests cover fail-closed cases.
7. Automated smoke for fixture learning loop; checklist item 9.
8. ADR + docs; TI doc M14 row fixed.
9. `./scripts/doctor.sh` and `./tests/run.sh` pass.

## Implementation checklist

- [x] Record approval; issue #111; rollback tag; feature branch
- [x] Learning-run model + CLI orchestrator
- [x] TI → staging export
- [x] Fixture sandbox harness + evidence templates
- [x] Unified `SKILL.md` + `capability.yaml` drafts
- [x] Similarity matcher → improvement proposals
- [x] Skill `skill-learning-loop`
- [x] Smokes, tests, ADR, checklist, docs
- [x] Validation evidence + PR

## Autonomy budget

See `.agent/budgets/m19-autonomous-skill-learning.md`.

| Limit | Value |
|---|---|
| Max iterations | 8 |
| Max failed validation cycles | 3 |
| Max weight-apply ops | 0 |
| Stop on scope change | true |

## Approval record

| Captain | Decision | Date |
|---|---|---|
| loganware | **APPROVED** — decisions #1–#6 locked | 2026-09-03 |

---

# M20 — Experience bridge + Captain-gated improvement apply (v1.24.0)

Issue: [#113](https://github.com/loganware05/captains-compass-cursor/issues/113)
Branch: `feature/113-m20-experience-bridge`
Rollback: `rollback/pre-m19-skill-learning` (M19 baseline) until M19 merges; then tag `rollback/pre-m20-experience-bridge`

## Acceptance criteria

1. `./scripts/bridge-learning-experiences.sh --run <learning-run.json>` writes Experiences.
2. `./scripts/run-skill-learning-loop.sh --record-experiences` attaches an experience-bridge section.
3. PROVEN still requires `--captain-approved` and ≥2 successful Experiences.
4. `./scripts/apply-skill-improvement.sh --proposal … --captain-approved` writes an improved draft; does **not** mutate live Skills unless `--apply-live`.
5. Excluded/meta Skills cannot be live-applied.
6. `approved_for_execution` remains false.

## Checklist

- [x] Experience bridge module + CLI
- [x] Optional `--record-experiences` on learning loop
- [x] PROVEN helper with captain + threshold gates
- [x] Apply-improvement CLI (draft default; `--apply-live` Captain-only)
- [x] Tests
- [x] Docs / ADR / Skill / PR

