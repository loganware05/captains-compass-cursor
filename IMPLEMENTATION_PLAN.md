# Implementation Plan

## Metadata

- Status: APPROVED
- Plan ID: p0-failclosed-budgets-ci
- Issue: [#26](https://github.com/loganware05/captains-compass-cursor/issues/26)
- Branch: `feature/26-p0-failclosed-budgets-ci`
- Created: 2026-07-30
- Last updated: 2026-07-30
- Approved by: Captain
- Approval date: 2026-07-30
- Approved revision: P0 plan as written; open questions resolved per recommendations (Markdown ledger; sandbox refresh after 1.2.0 merge before P1; one always-on budget bullet)
- Rollback checkpoint: `rollback/pre-p0-failclosed-budgets-ci` (`a6a7882`)

## Request

Implement **P0** from the production-orchestration gap analysis:

1. Fail-closed critical safety hooks
2. Autonomy budget mechanics (ledger + stop report + Skills/rules)
3. Control-repository CI (`doctor` + `tests`)

After P0 is complete (merged, validated, plan COMPLETE), proceed with **separate**
approval-gated plans for P1 then P2 (not in this change).

## Problem Statement

Compass’s control plane is policy-strong but sensor-soft:

- All hooks use `failClosed: false`, so a crashed/unrunnable hook silently
  allows product edits, secret staging, or protected-branch mutations.
- Autonomy budgets exist in design docs, plan templates, and sandbox evidence,
  but there is no machine-readable ledger, Skill procedure, or installer layout
  that forces a Budget Stop Report when limits are hit.
- The control repo has no GitHub Actions workflow; harness regressions only
  surface if someone runs `./tests/run.sh` locally.

## Desired Outcome

1. Critical hooks deny when the hook process fails or returns unusable output
   (`failClosed: true`).
2. Soft/optional hooks remain fail-open so formatting/test/PR-evidence friction
   does not freeze Captain workflows when tooling is absent.
3. Approved plans get a budget ledger under `.agent/budgets/`; agents update it
   each iteration and must stop with a Budget Stop Report when any limit is hit.
4. Control CI runs doctor + automated tests on PRs and pushes to `main`.
5. VERSION bumps to **1.2.0** (minor: safer defaults + additive budget package).
6. ADR supersedes ADR-005’s “fail-open initially” for critical hooks.
7. Docs/memory updated; evidence recorded; P1/P2 queued in PROGRESS only.

## Acceptance Criteria

### A. Fail-closed hooks

- [x] `.cursor/hooks.json` sets `failClosed: true` for:
  - `secret-protection`
  - `protected-branch`
  - `plan-approval-check`
- [x] Remaining hooks stay `failClosed: false`:
  - `branch-name-validation`
  - `pre-commit-formatting`
  - `pre-push-tests`
  - `pr-evidence-validation`
- [x] `.cursor/hooks/README.md` documents the critical vs soft split and why.
- [x] `tests/run.sh` asserts the three critical hooks are `failClosed: true` and
      the four soft hooks are `failClosed: false` (parse `hooks.json`).
- [x] ADR-014 records the decision (supersedes the fail-open portion of ADR-005
      for critical hooks only).

### B. Autonomy budget mechanics

- [x] Installer creates `.agent/budgets/` (alongside `.agent/evidence/`).
- [x] Template files installed or documented:
  - `templates/agent/BUDGET_LEDGER.md` (or YAML) — per-plan ledger shape
  - `templates/agent/BUDGET_STOP_REPORT.md` — stop report shape
- [x] New Skill `.cursor/skills/autonomy-budget/SKILL.md` covering:
  - Create ledger when plan becomes APPROVED (from plan Autonomy Budget section)
  - Increment iteration / failed-validation counters after each cycle
  - Stop and write Budget Stop Report when any limit is reached
  - Estimated cost labeled when exact spend is unavailable
- [x] `templates/docs/IMPLEMENTATION_PLAN.md` Autonomy Budget section references
      the ledger path and required stop fields.
- [x] Core rule or AGENTS wording explicitly requires the ledger + stop report
      (minimal rule edit; prefer Skill for procedure detail).
- [x] `scripts/doctor.sh` checks Skill presence and that budget templates exist
      in the control repo (and that installer creates `.agent/budgets/`).
- [x] `tests/run.sh` covers: Skill installed; `.agent/budgets/` created by
      install; optional smoke that ledger template is present in control repo.
- [x] `.gitignore` guidance keeps private budget notes out of git if needed
      (prefer committed ledgers for audit; private estimates under
      `.agent/budgets/private/` if Captain chooses).

### C. Control CI

- [x] `.github/workflows/ci.yml` runs on:
  - `pull_request` to `main`
  - `push` to `main`
- [x] Job steps: checkout → `./scripts/doctor.sh` → `./tests/run.sh`
- [x] Uses a maintained `ubuntu-latest` runner; no secrets required.
- [x] README / TESTING.md document how CI maps to local commands.
- [x] Workflow is intentionally control-repo only (no product-repo CI template
      in P0 — that is P1 evidence-matrix / templates territory if desired).

### D. Release hygiene / memory

- [x] `VERSION` → `1.2.0`
- [x] `CHANGELOG.md`, `PROGRESS.md`, `PROJECT_CONTEXT.md` updated
- [x] Evidence under `.agent/evidence/p0-failclosed-budgets-ci/`
- [x] GitHub issue + feature branch + rollback tag + PR to `main`
- [ ] Sandbox refresh to 1.2.0 via sandbox issue/PR after control merge
      (same pattern as v1.1.0)

## Non-Goals (this plan)

- P1: Cursor phase commands, evidence matrix by change type, multi-runtime
  `AGENTS.md` / `CLAUDE.md` adapters
- P2: Golden-agent evals, harness GC Skill, session/cost telemetry product,
  structural-test examples, young-package supply-chain harden
- Changing soft hooks to fail-closed
- Building a real token-cost API integration
- Auto-evolving rules/Skills without Captain approval
- Product-repo GitHub Actions templates (defer unless trivially a docs stub)

## Assumptions

1. Cursor honors `failClosed: true` for `beforeShellExecution` and `preToolUse`
   as documented; if IDE behavior differs, we record evidence and may need a
   follow-up fix without weakening policy intent.
2. Budget enforcement remains **agent-procedural** (Skill + rules), not a new
   Cursor hook that can read iteration count from the model runtime—because
   Cursor does not expose spend/iteration counters to hooks today.
3. Semver: safer defaults + additive Skill/templates = minor `1.2.0`.
4. Captain will approve P1 and P2 as separate plans after P0 COMPLETE.

## Open Questions

1. **Budget ledger format:** Markdown (human-auditable, matches Compass docs)
   vs YAML (machine-parseable)?  
   **Recommendation:** Markdown ledger with a stable heading/field schema;
   optional `doctor`/test regex checks for required fields.
2. **Sandbox timing:** Refresh disposable sandbox in the same control PR cycle
   (post-merge follow-up) vs wait for P1?  
   **Recommendation:** Post-merge sandbox refresh to 1.2.0 before starting P1,
   so P1 builds on verified P0 installs.
3. **Always-on rule edit:** Add a short always-on bullet for budget ledger path,
   or keep procedure only in the Skill + AGENTS?  
   **Recommendation:** One short always-on bullet in
   `03-validation-definition-of-done.mdc` pointing at `.agent/budgets/` + stop
   report; full procedure in the Skill.

## Current-State Analysis

| Area | Current | Gap |
|---|---|---|
| `hooks.json` | All 7 hooks `failClosed: false` | Critical path not fail-closed |
| ADR-005 | Explicitly chose fail-open initially | Needs supersession for critical hooks |
| Budgets | Fields in plan template; sandbox manual report | No Skill, no `.agent/budgets/`, no installer layout |
| CI | None (no `.github/workflows`) | No PR gate on doctor/tests |
| VERSION | `1.1.0` | Ready for `1.2.0` after P0 |

## Proposed Architecture

```text
.cursor/hooks.json
  critical → failClosed: true
  soft     → failClosed: false

.agent/budgets/<plan-id>.md     # live ledger (product repos)
.agent/evidence/.../budget-stop-report.md

.cursor/skills/autonomy-budget/SKILL.md
templates/agent/BUDGET_LEDGER.md
templates/agent/BUDGET_STOP_REPORT.md

.github/workflows/ci.yml        # doctor + tests
```

Flow after plan APPROVED:

1. First Mate creates `.agent/budgets/<plan-id>.md` from plan Autonomy Budget.
2. Each implementation/validation cycle updates counters.
3. On limit → write Budget Stop Report under evidence; stop; ask Captain.
4. Hooks continue to gate file/shell mutations independently of budgets.

## Workstreams

| ID | Workstream | Files (primary) | Parallel? |
|---|---|---|---|
| W1 | Fail-closed hooks + ADR + hook tests | `.cursor/hooks.json`, hooks README, `DECISIONS.md`, `tests/run.sh` | Yes vs W3 |
| W2 | Autonomy budget Skill/templates/installer/doctor | Skill, templates, `install.sh`, `doctor.sh`, rules/AGENTS, tests | Sequential after W1 interface stable |
| W3 | Control CI + VERSION/docs/memory | `.github/workflows/ci.yml`, VERSION, CHANGELOG, PROGRESS, TESTING, README | Yes vs W1 |

File overlap on `tests/run.sh` / docs → prefer **sequential commits** on one
branch rather than parallel worktrees unless W3 is isolated to `.github/` only
until final docs commit.

## Parallelization Plan

Single feature branch. Optional: land W3 workflow file early for CI signal while
W1/W2 finish. No multi-worktree split required (shared `tests/run.sh`).

## Files Expected to Change

- `.cursor/hooks.json`
- `.cursor/hooks/README.md`
- `.cursor/skills/autonomy-budget/SKILL.md` (new)
- `.cursor/rules/03-validation-definition-of-done.mdc` (minimal)
- `templates/docs/IMPLEMENTATION_PLAN.md`
- `templates/docs/AGENTS.md` (brief budget pointer)
- `templates/agent/BUDGET_LEDGER.md` (new)
- `templates/agent/BUDGET_STOP_REPORT.md` (new)
- `scripts/install.sh`
- `scripts/doctor.sh`
- `tests/run.sh`
- `.github/workflows/ci.yml` (new)
- `VERSION`, `CHANGELOG.md`, `PROGRESS.md`, `PROJECT_CONTEXT.md`, `DECISIONS.md`
- `TESTING.md`, `README.md` (CI + budget notes)
- `.agent/evidence/p0-failclosed-budgets-ci/`
- Possibly `scripts/update.sh` notes if new Skill count / paths need doctor sync

## Testing Strategy

1. `./scripts/doctor.sh` — green with new Skill + templates
2. `./tests/run.sh` — existing cases + failClosed assertions + budget install paths
3. Manual: confirm CI workflow YAML validates (`actionlint` if available; else
   push to PR and confirm GitHub check)
4. Record transcripts under `.agent/evidence/p0-failclosed-budgets-ci/`
5. After merge: sandbox `update.sh` to 1.2.0; doctor + sandbox tests

## Security Review

- Fail-closed on secret + protected-branch + plan-approval **reduces** bypass risk.
- CI must not print secrets; none required.
- Budget ledgers must not store API keys or raw `.env` contents.

## Accessibility Review

Not applicable (control-plane / docs / CI only).

## Migration Plan

- Product repos pick up fail-closed + new Skill via `update.sh` after 1.2.0 tag.
- Existing product repos without `.agent/budgets/` get the directory on update
  (installer/update should `mkdir -p`).
- Memory docs are never clobbered; new templates only appear if missing where
  that is the existing install policy—budget templates may live only in control
  repo and be copied into `.agent/budgets/_templates/` on install/update.

## Deployment Plan

1. Merge PR to `main`
2. Tag/release `v1.2.0` per `docs/RELEASE_CHECKLIST.md`
3. Refresh disposable sandbox to 1.2.0 via sandbox PR
4. Only then open the P1 implementation plan

## Rollback Plan

- Revert the release PR / tag if needed.
- Rollback checkpoint tag before implementation:
  `rollback/pre-p0-failclosed-budgets-ci`
- Product repos can pin previous Compass version (`v1.1.0`) via documented
  forward-upgrade path (downgrades remain unsupported; restore from backup/
  previous commit if required).

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Fail-closed hooks block Captains when Cursor hook runner is flaky | Soft hooks stay open; document `COMPASS_*` skips only for soft shell hooks; critical hooks should fail closed—if IDE false-denies, capture evidence and patch hook scripts, not policy |
| Agents ignore budget Skill | Always-on one-liner + plan template path + doctor Skill presence; sandbox budget exercise remains the behavioral proof |
| CI flakes on runner | Keep job minimal (bash + python3); no npm install required for control tests |
| Scope creep into P1/P2 | Explicit non-goals; PROGRESS lists P1/P2 as next after COMPLETE |

## Autonomy Budget

- Maximum iterations: 8
- Maximum failed validation cycles: 3
- Maximum estimated cost: moderate (single control-repo change set)
- Maximum elapsed time: 4 hours wall-clock across sessions
- Stop on scope change: true (P1/P2 require new plans)
- On stop: Budget Stop Report under `.agent/evidence/p0-failclosed-budgets-ci/`

## Definition of Done

- All acceptance criteria checked
- Doctor + tests green locally and on CI
- ADR-014 accepted in `DECISIONS.md`
- VERSION 1.2.0 + changelog + memory updated
- PR merged; release process started or completed per checklist
- Sandbox refresh issue opened or completed
- This plan status set to COMPLETE
- P1 plan not started until Captain approval of a new `IMPLEMENTATION_PLAN.md`

## Sequenced Follow-Ons (not this plan)

After P0 COMPLETE:

1. **P1 plan** — phase Cursor commands; evidence matrix by change type;
   multi-runtime AGENTS adapters
2. **P2 plan** — golden-agent evals; harness GC; session ledger; structural-test
   examples; young-package supply-chain harden

## Approval Record

- Approved by: Captain
- Approval date: 2026-07-30
- Approved revision: P0 as written; Markdown ledger; sandbox refresh after 1.2.0 before P1; always-on budget bullet
- Issue: #26
- Branch: `feature/26-p0-failclosed-budgets-ci`
- Rollback: `rollback/pre-p0-failclosed-budgets-ci` (`a6a7882`)
