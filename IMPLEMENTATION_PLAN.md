# Implementation Plan — Bend #278 Leftovers

- Status: **COMPLETE**

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain |
| Approved at | 2026-11-23 |
| Defaults | Q1=yes leftovers → v1.93.0; Q2=3 waves; Q3=keep #278; Q4=CI green without Bend; Q5=no B4/XRV |
| Rollback | `rollback/pre-bend-278-leftovers` @ `49e29c6` |
| Branch | `feature/278-bend-leftovers` |
| Worktree | `/Users/loganware/Documents/Personal/Code/captains-compass-bend-278` |


## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `bend-278-leftovers` |
| Issue | [#278](https://github.com/loganware05/captains-compass-cursor/issues/278) (reuse) |
| Baseline | `origin/main` @ `49e29c6` / product **v1.92.0** @ `3465f7f` |
| Branch | `feature/278-bend-leftovers` from `main` |
| Rollback | `rollback/pre-bend-278-leftovers` (tag at baseline after approval) |
| Proposed release | **v1.93.0** (minor — close parked formal gaps) |
| Created | 2026-11-22 |
| Source | Post-v1.92.0 Proceed; scout pick among deferred backlog |

Budget: `.agent/budgets/bend-278-leftovers.md`  
Durable copy: `docs/plans/BEND_278_LEFTOVERS.md`

**Prior plan:** `specialized-real-local-eval` **COMPLETE** (v1.92.0 / #306 + closeout #307).

## Request

Close the three leftovers parked under ADR-110 / #278 after P12:
1. P4/P5 whole-history (or sequence) lift
2. Lean SHA/version pin
3. Opt-in CI wiring for `--strict-laws` / law-integrity (default CI stays green without Bend)

Defer B4 FIX→SUBMIT and XRV ops-verified.

## Why this slice

| Candidate | Verdict |
|---|---|
| **#278 leftovers** | **Recommended** — formal suite exists; gaps named; lowest external-ops |
| B4 FIX→TEST→SUBMIT | Defer — intentional write blast into allowlisted repos |
| XRV ops-verified | Defer — needs real deploy evidence |

## Current implementation (verified)

| Area | State |
|---|---|
| P4/P5 | Per-step only (`LAWS.bend`); P3′ already sequence-shaped |
| Lean pin | Unpinned; Bend pin optional (`COMPASS_BEND_SHA256`) |
| `--strict-laws` | CLI works; **not** in `.github/workflows/ci.yml` |
| Evidence | `.agent/evidence/bend-adr-110-go/report.json` lists these three gaps |
| Issue | [#278](https://github.com/loganware05/captains-compass-cursor/issues/278) OPEN |

## Desired behavior

1. Whole-history / sequence P4/P5 (or Captain Amendment if unprovable without weakening per-step laws).
2. Fail-closed Lean pin in toolchain discovery.
3. Opt-in CI job/step for law-integrity / `--strict-laws` that does **not** require Bend binary for default green.
4. ADR-110 boundary amended; docs/evidence updated; #278 closed or narrowed.

## Scope

### In scope (3 waves)

| Wave | Work |
|---|---|
| W1 | P4/P5 whole-history laws + proofs + lock |
| W2 | Lean SHA/version pin |
| W3 | Opt-in CI `--strict-laws` / law-integrity; docs + evidence |

### Out of scope / deferred

- B4 FIX write/apply/PR automation
- XRV `operationally_verified` / deploy drills
- #237 Level 3 / paid GPU
- Widening formal targets beyond `policy-lifecycle`
- Making Bend a required CI dependency
- Weakening existing per-step P4/P5

## Acceptance criteria

- [x] P4/P5 whole-history shipped **or** documented Captain Amendment with evidence.
- [x] Lean pin fail-closed when configured; mismatch refused.
- [x] CI has opt-in law-integrity path; default doctor/`tests/run.sh` green without Bend.
- [x] ADR-110 / bend docs updated; evidence under `.agent/evidence/bend-278-leftovers/`.
- [ ] PR from `main` (opening); rollback tag cited; authority locks remain false.

## Validation

- Formal check with Bend+Lean when available
- Unit: `tests/orchestrator/test_formal_policy_lifecycle.py`
- Full: doctor, `tests/run.sh`
- CI: new opt-in path dry-run / job config review

## Risks & assumptions

| Risk | Mitigation |
|---|---|
| Whole-history proofs too hard | Stop + Captain Amendment; still ship Lean pin + CI |
| ADR-110 said no CI wire | Explicit amend under this approved plan |
| Law changes trip `--strict-laws` | Document expected change vs base; Captain-owned file gate |

## Open questions (Captain)

1. **Q1 — Ship `bend-278-leftovers` as next product plan @ v1.93.0?** Recommended: **yes**.
2. **Q2 — One plan, three waves** (laws → Lean pin → CI)? Recommended: **yes**.
3. **Q3 — Keep issue #278** (do not open a new issue)? Recommended: **yes**.
4. **Q4 — Default CI must stay green without Bend binary?** Recommended: **yes**.
5. **Q5 — Prefer B4 or XRV instead?** Recommended: **no**.

## Required Capabilities

- formal-methods (Bend), testing-validation, github-integration, documentation

## Reusable Capabilities Found

| Skill | Role |
|---|---|
| Existing `formal/` + `orchestrator/formal/` | Leftover home |
| `testing-validation` | Suite + CI |
| `github-integration` | #278 / PR |

## Technology Intelligence Candidates

*None queried.*

## Task Graph (human)

| Task ID | Objective | Dependencies |
|---|---|---|
| `task-p45` | Whole-history P4/P5 or Amendment | — |
| `task-lean-pin` | Lean SHA/version pin | task-p45 (or parallel if Amendment) |
| `task-ci` | Opt-in strict-laws CI | task-lean-pin |
| `task-docs` | ADR/docs/evidence/#278 | task-ci |

## Autonomy budget (proposed)

| Limit | Value |
|---|---|
| Max iterations | 14 |
| Max wall time | 5 hours |

## Approval Boundary

**Approved.** Implementation in progress under autonomy budget `bend-278-leftovers`.
