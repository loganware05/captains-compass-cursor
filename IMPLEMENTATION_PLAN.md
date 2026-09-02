# Implementation Plan — Autonomous Skill Learning Loop (M19+)

- Status: **AWAITING APPROVAL**
- Plan ID: `m19-autonomous-skill-learning`
- Issue: TBD (create after approval)
- Baseline: v1.22.0 (`3c4455e` on `main`)
- Prior backlog: M13–M18 / post-foundation **COMPLETE**

| Field | Value |
|---|---|
| **Plan ID** | `m19-autonomous-skill-learning` |
| **Status** | **AWAITING APPROVAL** |
| **Baseline** | v1.22.0 (`3c4455e`) |
| **Issue** | TBD after approval |
| **Target release** | **v1.23.0** (M19); optional follow-ons v1.24.0+ |
| **Branch** | `cursor/m19-autonomous-skill-learning-9568` (plan); feature branch after approval |
| **Rollback** | Tag `rollback/pre-m19-skill-learning` at approval time |
| **Captain approval** | — |

## Problem statement

M13–M18 shipped the pieces of a learning system in isolation:

- **M14** batch-categorizes GitHub Stars (`categorize-github-stars.sh` → `github-stars-categorized`)
- **candidate-promotion** / **skill-lifecycle** advance candidates through `SANDBOX_TESTED` → `PROVEN_SKILL`
- **experience-skill-training** drafts Skills from Experiences
- **M18** release smokes prove fixture CLIs exist

What is missing is a **closed, Captain-gated loop** that uses categorized Stars inside the disposable sandbox to:

1. Select high-signal candidates by category
2. Export them to staging
3. Run a **sandbox candidate / draft-Skill test** (evidence-backed)
4. Emit unified Skill drafts
5. Stop for Captain review before any live Skill install

Today an operator must manually glue those CLIs. There is no TI → staging export, no per-candidate sandbox harness, and no shared “learning run” artifact. Draft quality is asymmetric (`promote --draft-skill` writes `capability.yaml` only; Experience training writes full `SKILL.md`).

## Desired behavior

After Captain-approved implementation:

1. Explicit CLI (e.g. `./scripts/run-skill-learning-loop.sh`) orchestrates, from fixtures or TI cache:
   - categorize Stars (reuse M14)
   - select top-N candidates by category + objective match
   - export schema-valid staging candidate JSON
   - run sandbox candidate harness → evidence under `.agent/evidence/candidate-sandbox-test/`
   - advance to `SANDBOX_TESTED` when evidence passes
   - emit unified draft (`SKILL.md` + `capability.yaml` + provenance) under `skill-drafts/`
   - **stop** — never auto-advance past Captain gates
2. Sandbox behavioral checklist gains an item for the skill-learning loop exercise.
3. M18-style automated smoke covers the fixture path of the loop (no LLM in CI).
4. Docs/ADR state clearly: **automated staging ≠ auto-install**.

## Non-goals (prohibited)

- Auto-merge or auto-copy into `.cursor/skills/`
- Setting `approved_for_execution: true`
- Cloning or executing starred/external repositories
- Running the full loop from hooks, workstream close, or CI defaults
- Weakening `--captain-approved` for `APPROVED` / `AVAILABLE_SKILL` / `PROVEN_SKILL`
- Live Stars / live Hub network calls in CI

## Captain decisions (need lock)

| # | Topic | Options | Recommendation |
|---|---|---|---|
| 1 | Autonomy meaning | **A)** Automated staging + sandbox evidence only (still Captain for live Skills) · **B)** Also auto-apply routing/context proposals under budget · **C)** Auto-install drafts into sandbox Skills dir (still not control-repo live) | **A** — matches ADR-018/025/030 safety model |
| 2 | Roadmap shape | **A)** Single M19 / v1.23.0 · **B)** Split M19 (orchestrator + export + harness) then M20 (Experience bridge + PROVEN feedback) | **B** if scope feels large; **A** if Captain wants one cohesive ship |
| 3 | Learning target | **A)** Draft **new** Skills from categorized star candidates · **B)** Improve **existing** Compass Skills (routing/proficiency) using category signals · **C)** Both (new drafts primary; category→routing proposals secondary) | **A** for M19; **C** deferred to M20 if split |
| 4 | Sandbox harness depth | **A)** Fixture-only candidate exercise (doctor + draft validation + evidence template) · **B)** Full interactive product exercise per candidate in disposable sandbox | **A** automated + interactive checklist row for Captain review (same pattern as M18) |
| 5 | Default input source | **A)** `fixtures` in CI / smokes · **B)** `ti-cache` when present · Captain may pass `--source live` locally | **A** for defaults; support all three sources like categorize CLI |

---

## Roadmap (proposed)

| Milestone | Version | Theme | Status |
|---|---|---|---|
| **M19** | v1.23.0 | Skill learning orchestrator + TI staging export + sandbox candidate harness + unified drafts | **Proposed** |
| **M20** *(optional)* | v1.24.0 | Experience bridge: learning-run → record Experiences → PROVEN path + category-informed routing proposals | Deferred pending Captain decision #2/#3 |
| **M21** *(optional)* | v1.25.0 | Sandbox interactive skill-improvement exercise + release-smoke expansion | Deferred |

---

# M19 — Autonomous Skill Learning Loop (v1.23.0) — PROPOSED

## Objective

Close the Captain-gated loop from **categorized GitHub Stars → sandbox-tested staging candidates → unified Skill drafts**, with fixture-safe automation and no weakening of promotion safety gates.

## Current behavior (evidence)

| Piece | Exists | Gap |
|---|---|---|
| `categorize-github-stars.sh` | Yes (M14) | Not chained |
| `github-stars-categorized` TI | Yes | Query does not write staging JSON |
| `promote-candidate.sh` | Yes | Needs pre-existing candidate file + manual evidence |
| `train-skill-from-experience.sh` | Yes | Disconnected from Stars path |
| Sandbox release smokes | Yes (M18) | Only asserts categorize CLI, not full loop |
| `SANDBOX_TESTED` semantics | Evidence path gate | No harness that produces that evidence |

## Acceptance criteria

1. Explicit `./scripts/run-skill-learning-loop.sh` (name finalizable) runs end-to-end on `--source fixtures` and exits 0 with artifacts under `.agent/`.
2. Loop writes staging candidates, sandbox-test evidence, and unified skill drafts; does **not** write under `.cursor/skills/`.
3. Promotion past `SANDBOX_TESTED` still requires `--captain-approved`.
4. `approved_for_execution` remains `false` on all candidates.
5. Unit tests cover fail-closed cases (missing evidence, attempt to install live, empty categorize output).
6. Automated smoke step registered for the fixture learning loop.
7. Behavioral checklist item for interactive Captain review of drafts.
8. ADR + Skill docs + TI integration doc (fix stale “Batch ML Deferred” row).
9. `./scripts/doctor.sh` and `./tests/run.sh` pass; evidence under `.agent/evidence/`.

## Affected systems

- `orchestrator/learning/` (new) — loop orchestration
- `orchestrator/promotion/` — TI→staging export; richer draft emitter
- `orchestrator/training/` — share draft writer with promotion path
- `orchestrator/providers/technology_intelligence/` — categorized selection helpers (read-only reuse)
- `orchestrator/release/sandbox_smokes.py` — new automated smoke
- `scripts/` — new CLI(s)
- `.cursor/skills/` — new Skill `skill-learning-loop` (or extend `candidate-promotion` + `experience-skill-training`; Captain choice)
- `docs/`, `DECISIONS.md`, `TESTING.md`, `docs/evals/SANDBOX_BEHAVIORAL_CHECKLIST.md`
- Sandbox refresh PR after control-repo release (pattern M13–M18)

## Independent workstreams

| ID | Stream | Files (approx) | Parallel? |
|---|---|---|---|
| W1 | Learning-run model + CLI orchestrator | `orchestrator/learning/*`, `scripts/run-skill-learning-loop.sh` | After W2 interface sketched |
| W2 | TI → staging export + unified draft emitter | `orchestrator/promotion/`, `orchestrator/training/` | Yes with W1 once contracts fixed |
| W3 | Sandbox candidate harness + evidence templates | `orchestrator/learning/sandbox_harness.py`, `.agent/evidence/_templates/` | Yes with W1 |
| W4 | Smokes, tests, docs, Skill, ADR | `tests/`, `docs/`, `.cursor/skills/`, `DECISIONS.md` | After W1–W3 |

## Implementation checklist (post-approval)

- [ ] Record approval; set status APPROVED; create GitHub issue
- [ ] Rollback tag `rollback/pre-m19-skill-learning`
- [ ] Feature branch `feature/<issue>-m19-skill-learning-loop`
- [ ] Learning-run schema/artifact under `.agent/learning-runs/`
- [ ] TI categorized → staging export helper
- [ ] Sandbox candidate harness (fixture-safe)
- [ ] Unified `SKILL.md` + `capability.yaml` draft emitter (Stars + Experience parity)
- [ ] `run-skill-learning-loop.sh` orchestrator (explicit only)
- [ ] Skill docs + ADR-035 (proposed number)
- [ ] Unit tests + M18 smoke catalog extension
- [ ] Behavioral checklist item 9
- [ ] Fix stale TI doc M14 status row
- [ ] Validation evidence + adversarial review
- [ ] Feature PR → release v1.23.0 → sandbox refresh

## Required capabilities (from `capability-plan.sh`)

Domains detected: `test`, `github`. No capability gaps for inferred requirements.

Top reusable Skills: `testing-validation`, `github-integration`, `pull-request-preparation`, plus learning stack `candidate-promotion`, `skill-lifecycle`, `experience-skill-training`, `technology-intelligence-live`, `compass-evaluator`, `bounded-autonomy`, `autonomy-budget`.

Machine artifacts: `.agent/plans/m19-autonomous-skill-learning/{resolve,task-graph,manifests}.json`

## Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only.

Planning used stub TI (CI default). Post-approval local demos should use:

```bash
./scripts/categorize-github-stars.sh --source fixtures
COMPASS_TI_PROVIDER=github-stars-categorized \
  ./scripts/capability-plan.sh --plan-id m19-demo "react forms accessibility"
```

## Task graph

| Task ID | Objective | Dependencies |
|---|---|---|
| `task-discovery` | Confirm promotion/training/categorize contracts | — |
| `task-architecture` | Learning-run schema, harness contract, ADR | task-discovery |
| `task-implementation` | Orchestrator, export, harness, drafts, CLI, Skill | task-architecture |
| `task-validation` | Unit tests, doctor, smokes, fail-closed cases | task-implementation |
| `task-documentation` | ADR, TI docs, checklist, PROGRESS, CHANGELOG | task-validation |

## Evaluation strategy

- Fixture learning-loop smoke green
- Fail-closed: no write to `.cursor/skills/`; captain gate intact
- Doctor + full `./tests/run.sh`
- Adversarial review of auto-install / execution-approval regressions
- Interactive sandbox checklist attestation for draft review

## Learning plan

Retain `.agent/plans/m19-autonomous-skill-learning/` artifacts. After M19 ships, first successful learning runs become fixtures for M20 Experience bridge (if approved).

## Autonomy budget (post-approval)

Track in `.agent/budgets/m19-autonomous-skill-learning.md`:

| Limit | Proposed |
|---|---|
| Max implementation iterations | 8 |
| Max weight-apply ops | 0 (unless Captain picks decision #1B) |
| Cost / time | Stop on budget; write Budget Stop Report |

## Migration / rollback

- No DB migrations
- New artifacts under `.agent/` only (gitignored runtime ok; fixtures committed)
- Rollback: tag `rollback/pre-m19-skill-learning`; revert feature PR; sandbox can stay on 1.22.0 until refresh

## Risks

| Risk | Mitigation |
|---|---|
| “Autonomous” misread as auto-install | ADR + Skill prohibited actions + tests asserting no live Skill writes |
| Draft quality too thin to be useful | Unify with Experience training template; include category + discovery_signal provenance |
| Scope creep into M20 routing | Decision #2/#3 locks; return to approval gate if expanded |
| Live Stars unavailable in cloud agents | Fixture + ti-cache sources; `live` Captain-local only |

## Assumptions

1. Disposable sandbox remains the interactive validation venue; control-repo owns orchestrator code.
2. M14 Naive Bayes + manual labels remain the categorization source (no new ML model in M19).
3. Captain will review Skill drafts via PR before any live `.cursor/skills/` install.
4. Cloud agent `gh` token cannot list user starred repos (403); CI/fixtures path is authoritative.

## Open questions for Captain

1. Lock decisions #1–#5 above.
2. Prefer **new Skill** `skill-learning-loop` vs extending existing Skills only?
3. Should M19 include a control-repo **demo fixture learning-run** committed under `tests/fixtures/learning/`?

---

## Approval boundary

**Implementation must not begin until the Captain explicitly approves this plan** (and locks the Captain decisions table).

Machine-generated capability matches and agent manifests are proposals only.

## Approval record

| Captain | Decision | Date |
|---|---|---|
| — | AWAITING APPROVAL | — |
