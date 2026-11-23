# Implementation Plan — XRV Ops-Verified Drill

- Status: **COMPLETE**

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain |
| Approved at | 2026-11-23 |
| Defaults | Q1=yes xrv-ops-verified → v1.94.0; Q2=hermetic-only; Q3=no B4; Q4=Bend CI optional |
| Issue | [#310](https://github.com/loganware05/captains-compass-cursor/issues/310) |
| Rollback | `rollback/pre-xrv-ops-verified` @ `4747994` |
| Branch | `feature/310-xrv-ops-verified` |
| Worktree | `/Users/loganware/Documents/Personal/Code/captains-compass-xrv-ops` |


## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `xrv-ops-verified` |
| Issue | [#310](https://github.com/loganware05/captains-compass-cursor/issues/310) |
| Baseline | `origin/main` @ `4747994` / product **v1.93.0** @ `06e7617` |
| Branch | `feature/<issue>-xrv-ops-verified` from `main` |
| Rollback | `rollback/pre-xrv-ops-verified` (tag at baseline after approval) |
| Proposed release | **v1.94.0** (minor — close XRV program exit criterion) |
| Created | 2026-11-23 |
| Source | Post-v1.93.0 Proceed; scout among B4 FIX→SUBMIT vs XRV ops-verified |

Budget: `.agent/budgets/xrv-ops-verified.md`  
Durable copy: `docs/plans/XRV_OPS_VERIFIED.md`

**Prior plan:** `bend-278-leftovers` **COMPLETE** (v1.93.0 / #308 + closeout #309).

## Request

Close the last open XRV program exit criterion: *independent auditor can reconstruct
full cycles including ops-verified states* (`docs/plans/XRV_CROSS_REPOSITORY_VALIDATION.md`).

Defer B4 live FIX→TEST→SUBMIT (write blast into allowlisted repos) and #237 Level 3.

## Why this slice (vs B4)

| Candidate | Verdict |
|---|---|
| **XRV ops-verified** | **Recommended** — last XRV checkbox; hermetic-first scaffolding; no write blast |
| B4 FIX→TEST→SUBMIT | Defer — intentional write/PR automation beyond packet MVP |
| Enable Bend CI var | Not a product plan — Captain sets `COMPASS_BEND_STRICT_LAWS_CI=1` (see note below) |

### Note: why Bend law integrity was SKIPPED on #308/#309

The job `bend-law-integrity` is **opt-in by design** (ADR-110 / plan Q4):

```yaml
bend-law-integrity:
  if: ${{ vars.COMPASS_BEND_STRICT_LAWS_CI == '1' }}
```

GitHub Actions marks the job **Skipped** when the repository variable
`COMPASS_BEND_STRICT_LAWS_CI` is unset or not exactly `1`. That is expected —
default CI must stay green without installing Bend/Lean on runners. The job is
wired and ready; enabling it is a Captain repo-settings action, not a code change.

To turn it on: GitHub → Settings → Secrets and variables → Actions → Variables →
add `COMPASS_BEND_STRICT_LAWS_CI` = `1`. Then PRs run
`northstar formal check policy-lifecycle --strict-laws --base-ref origin/main`
(fails closed on LAWS/SPEC drift even without a Bend binary).

## Current implementation (verified)

| Area | State |
|---|---|
| XRV W1–W3 + Pilot C | Shipped (v1.83.1–v1.85.0 + PrizePicks) |
| Readiness / portfolio | Hermetic scorecards; `ops_verified` not a first-class EER/cycle state |
| EER validate | Gated `COMPASS_XRV_EER_ENABLED` |
| Open exit criterion | “reconstruct full cycles incl. ops-verified states” still unchecked |
| B4 | Packet MVP shipped (v1.35.0); FIX→SUBMIT still prepare-only |

## Desired behavior

1. First-class **ops-verified** evidence/state in the XRV EER (or adjacent) model.
2. Hermetic fixture(s) proving an auditor can reconstruct a cycle that includes that state.
3. CLI/docs path to record or validate ops-verified evidence (gated; no authority grant).
4. Optional Wave 2: Captain-supplied live deploy/smoke path — only if approved in Qs.
5. Mark XRV program exit criterion done; authority locks remain false.

## Scope

### In scope (2 waves)

| Wave | Work |
|---|---|
| W1 | Schema + hermetic reconstruction fixture + validate path + tests |
| W2 | Docs / XRV plan checkbox / evidence; optional gated live drill if Q2=yes |

### Out of scope / deferred

- B4 live FIX apply / draft-PR automation
- #237 Level 3 / paid GPU
- Making Bend a required CI dependency
- Auto-promoting readiness or inventing ops scores
- Production deploys without Captain-provided evidence

## Acceptance criteria

- [ ] Ops-verified state/record is schema-validated and documented.
- [ ] Hermetic fixture reconstructs a full cycle including ops-verified.
- [ ] Gated CLI or assess path; default doctor/`tests/run.sh` green without live deploy.
- [ ] XRV plan exit criterion checked; evidence under `.agent/evidence/xrv-ops-verified/`.
- [ ] PR from `main`; rollback tag cited; `approved_for_execution` / `authority_mutation` false.

## Validation

- Unit: EER/ops-verified schema + reconstruction
- Full: doctor, `tests/run.sh`
- Optional live: only if Q2 approved and Captain provides evidence paths

## Risks & assumptions

| Risk | Mitigation |
|---|---|
| “Ops-verified” undefined | W1 defines minimal evidence contract (smoke id + timestamp + repo SHA) |
| Live drill blocked | Ship hermetic W1 alone; park live as follow-up |
| Confusion with readiness pillars | Keep ops-verified on EER/cycle surface, not invented readiness scores |

## Open questions (Captain)

1. **Q1 — Ship `xrv-ops-verified` as next product plan @ v1.94.0?** Recommended: **yes**.
2. **Q2 — Hermetic-first only this release** (live deploy drill deferred)? Recommended: **yes**.
3. **Q3 — Prefer B4 FIX→SUBMIT instead?** Recommended: **no**.
4. **Q4 — Also set `COMPASS_BEND_STRICT_LAWS_CI=1` now?** Recommended: **optional** (ops toggle, not this PR).

## Required Capabilities

- testing-validation, documentation, github-integration

## Reusable Capabilities Found

| Skill / surface | Role |
|---|---|
| `orchestrator/xrv/` + EER validate | Home for ops-verified |
| `testing-validation` | Fixtures + suite |
| Existing XRV docs/plans | Exit criterion source |

## Technology Intelligence Candidates

*None queried.*

## Task Graph (human)

| Task ID | Objective | Dependencies |
|---|---|---|
| `task-schema` | Ops-verified schema + fixture | — |
| `task-validate` | Gated validate/reconstruct path | task-schema |
| `task-docs` | XRV plan checkbox + evidence | task-validate |

## Autonomy budget (proposed)

| Limit | Value |
|---|---|
| Max iterations | 12 |
| Max wall time | 4 hours |

## Approval Boundary

**Approved.** Implementation in progress under autonomy budget `xrv-ops-verified`.


## Completion

| Field | Value |
|---|---|
| Completed at | 2026-11-23T20:18:18Z |
| Proposed version | **v1.94.0** |
| Validation | `test_xrv_ops_verified` + hermetic validate/reconstruct CLI |
| Live deploy | Deferred (Captain Q2) |
