# Implementation Plan — M51 / Kimi K3 Project Overseer

## Metadata

- Status: APPROVED

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m51-project-overseer` |
| Approved | 2026-10-11 — Captain: "I approve" (accepts recommended decisions 1–6) |
| Linear | [OVA-67](https://linear.app/ovaltechnologysolutions/issue/OVA-67/m51-kimi-k3-project-overseer-v1560) · Milestone **M51 — Kimi K3 Project Overseer** |
| Spec source | [Notion: Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M51 section) |
| Notion plan mirror | [M51 Implementation Plan](https://app.notion.com/p/3f6e6a901c438131b2aacb3b7e1224c2) |
| Linear project | [NorthStar Behavioral Intelligence Loop](https://linear.app/ovaltechnologysolutions/project/northstar-behavioral-intelligence-loop-e24174b3f1ef) (P-OVA-4) |
| Prerequisite | **M50 merged** — PR [#193](https://github.com/loganware05/captains-compass-cursor/pull/193) → **v1.55.0** @ `5d108db`; OVA-66 Done |
| Supersedes | Completed plan `m50-policy-promotion-lifecycle` |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.55.0** @ `5d108db` |
| Prepared | 2026-10-11 |
| Proposed release | **v1.56.0** |
| Rollback | Tag `rollback/pre-m51-project-overseer` @ `5d108db` |
| Proposed branch | `feature/OVA-67-m51-project-overseer` |
| Capability plan | `.agent/plans/m51-project-overseer/` |
| Captain | Logan Ware |

## Request

Continue the Behavioral Intelligence Loop after M50. Establish **M51 Project
Overseer**: a read-oriented `northstar status` surface that snapshots repository
reality, explains current understanding, compares evolution, and drafts
reconciliation proposals for documentation/project-memory drift — without
gaining mutating authority.

## Current state (evidence)

| Track | Reality |
|---|---|
| M46–M50 | Shipped through **v1.55.0** (#193 on `main`) |
| M51 | Linear milestone exists; issue **OVA-67** created; plan awaiting approval |
| Existing reconcile | `reconcile-northstar-run.sh` is Learning-Loop run reconcile — **not** Overseer |
| Kimi K3 | No live provider wiring in control repo yet |

## Problem Statement

NorthStar accumulates project memory (`VERSION`, `PROJECT_CONTEXT.md`,
`PROGRESS.md`, Skill/agent counts, ADRs) that can drift from repository reality.
Operators cannot yet:

1. Snapshot a structured “current understanding” of the control/product repo
2. Explain architecture / active work from memory + filesystem signals
3. Compare understanding across git SHAs
4. Draft reconcile proposals when docs disagree with reality (e.g. VERSION vs
   prose counts)

Without M51, drift is discovered ad hoc (as the Notion sprint already noted).

## Desired Outcome

```
repo reality + project memory
  → status snapshot (schema-validated)
  → explain / compare --since <sha>
  → reconcile → proposal drafts only
  → northstar status …
  → evidence under .agent/evidence/m51-project-overseer/
```

No path may approve plans, promote Skills/Policies, alter routing, merge,
deploy, or silently rewrite canonical memory docs.

## Decision Summary

| Principle | Implication |
|---|---|
| Read-oriented | Overseer inspects and proposes; never authorizes |
| Hermetic CI first | Deterministic drift detectors; no live Kimi required |
| Proposal-only reconcile | Write drafts under `.agent/status/reconcile-proposals/` |
| Dual enable gate | Env flag (default off) **and** explicit CLI |
| Fail closed | Missing inputs / invalid snapshot → no authority mutation |
| Distinct from run reconcile | Do not overload `reconcile-northstar-run.sh` |
| Version | **v1.56.0** |

## Resolved Decisions (Captain — 2026-10-11)

| # | Decision |
|---|---|
| 1 | Top-level **`northstar status`** |
| 2 | New **`COMPASS_STATUS_ENABLED`** (default off) |
| 3 | **Deterministic drift first** + stub provider interface (no live Kimi in CI) |
| 4 | Persist under **`.agent/status/`** |
| 5 | Reconcile **proposals only** (no auto memory rewrite) |
| 6 | Release **v1.56.0** |

## Approval Record

Captain Logan Ware — 2026-10-11 — "I approve" (recommended decisions 1–6 accepted).

## Scope

### In (M51)

1. Schemas: `project-status-snapshot.schema.json` + `status-reconcile-proposal.schema.json` — fail-closed (`approved_for_execution: false`, `authority_mutation: false`)
2. Package `orchestrator/status/` — snapshot, explain, compare, drift detectors, reconcile proposals, service
3. Deterministic drift checks (initial set):
   - `VERSION` file vs mentions / implied version in `PROGRESS.md` current status
   - Skill directory count vs Skill count prose in `PROJECT_CONTEXT.md` (when countable)
   - `IMPLEMENTATION_PLAN.md` Status vs `PROGRESS.md` active plan consistency
   - Presence of required memory docs (`AGENTS.md`, `PROJECT_CONTEXT.md`, `DECISIONS.md`, `PROGRESS.md`, `TESTING.md`)
4. Persist snapshots under `.agent/status/snapshots/`; proposals under `.agent/status/reconcile-proposals/`
5. `northstar status` CLI: `snapshot`, `explain`, `compare`, `reconcile`, `export`
6. Enable gate: `COMPASS_STATUS_ENABLED` (default off) **and** explicit CLI
7. Hermetic fixtures + unit/integration tests
8. Docs: ADR-073, TESTING, PROGRESS, PROJECT_CONTEXT, CHANGELOG, VERSION → 1.56.0
9. Evidence under `.agent/evidence/m51-project-overseer/`
10. Doctor smoke: fail-closed when flag unset
11. Optional stub provider interface `StatusProvider` (`stub` only in v1.56.0) for future Kimi

### Out (Non-Goals)

- Live Kimi K3 / OpenRouter calls in CI
- Auto-apply reconcile to memory docs / ADRs
- Approving plans, promoting Skills/Policies, routing mutation
- Merge / deploy / release automation
- Replacing `reconcile-northstar-run.sh` (Learning Loop)
- Database / Prisma / frontend

## Proposed Architecture

```
scripts/northstar status …
        │
        ▼
scripts/run-status.sh
        │
        ▼
orchestrator/status/
  snapshot.py / explain.py / compare.py / drift.py / reconcile.py / service.py
  providers/stub.py   # future: kimi.py
        │
        ▼
.agent/status/snapshots/<snapshot-id>.json
.agent/status/reconcile-proposals/<proposal-id>/
(+ evidence under .agent/evidence/m51-project-overseer/)
```

### Operator surface (proposed)

```bash
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status explain --repo .
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status compare --since HEAD~5 --repo .
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status reconcile --repo .
```

## Capability / Agent Plan (adjusted)

Capability planner emitted an irrelevant docker-heavy graph; **override**:

| Task | Profile | Notes |
|---|---|---|
| discovery | `repository-scout` | Locate memory docs + VERSION/Skill count seams |
| architecture | `architecture-agent` | Snapshot schema + drift contracts |
| implementation | `implementation-agent` | `orchestrator/status/` + CLI (no UI/Docker) |
| validation | `test-engineer` | Hermetic unit/integration + doctor |
| documentation | `documentation-agent` | ADR/PROGRESS/VERSION/Linear |

Machine artifacts: `.agent/plans/m51-project-overseer/`.

## Files to Add / Modify

### Add

| Path | Purpose |
|---|---|
| `orchestrator/status/` | Overseer package |
| `orchestrator/schemas/project-status-snapshot.schema.json` | Snapshot contract |
| `orchestrator/schemas/status-reconcile-proposal.schema.json` | Proposal contract |
| `scripts/run-status.sh` | Enable-gated runner |
| `tests/fixtures/status/` | Hermetic fixtures |
| `tests/orchestrator/test_m51_project_overseer.py` | Tests |
| `docs/plans/M51_PROJECT_OVERSEER.md` | Plan archive |
| `.agent/budgets/m51-project-overseer.md` | Autonomy budget |
| `.agent/evidence/m51-project-overseer/` | Validation evidence |
| `.agent/status/` layout | Snapshots + proposals |

### Modify (thin)

| Path | Change |
|---|---|
| `orchestrator/behavior/enabled.py` **or** new `orchestrator/status/enabled.py` | Status enable gate |
| `scripts/northstar` | Dispatch `status` |
| `scripts/doctor.sh` | Fail-closed smoke |
| `orchestrator/schemas/validate.py` | Register schemas |
| `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `PROJECT_CONTEXT.md`, `DECISIONS.md`, `VERSION` | M51 docs/release |

### Explicit non-touch

- No Policy Active auto-apply changes
- No AHF live-execution enablement
- No live Kimi keys in fixtures

## Acceptance Criteria

- [x] `northstar status snapshot|explain|compare|reconcile` behind enable gate
- [x] Deterministic drift detectors produce schema-valid findings hermetically
- [x] Reconcile writes proposal drafts only; never mutates memory docs in-place
- [x] Schemas reject `approved_for_execution: true` / `authority_mutation: true`
- [x] No Skill/Policy/routing/plan-approval mutation
- [x] Doctor/tests green; no live Kimi required
- [x] Evidence + ADR-073 + VERSION 1.56.0
- [x] Linear OVA-67 linked

## Test Matrix

| Layer | Coverage |
|---|---|
| Unit | Drift detectors, schema locks, enable gate |
| Integration | CLI snapshot/explain/compare/reconcile against fixtures |
| Regression | M46–M50 suites unchanged |
| Security | No memory auto-write; fail-closed gates |
| Doctor | Flag unset → status unavailable |

## Rollback Plan

1. Tag `rollback/pre-m51-project-overseer` @ `5d108db` after approval
2. Revert M51 PR / reset to tag
3. Remove `.agent/status/` operator artifacts if needed
4. VERSION / docs roll back with the revert

## Autonomy Budget

| Limit | Value |
|---|---|
| Max iterations | 8 |
| Max wall time | 4 hours |
| Stop on | Illegal authority mutation, failing security invariants, budget exhaustion |

Track in `.agent/budgets/m51-project-overseer.md`.

## Security Considerations

- Dual enable gate
- Proposal-only reconcile
- No secrets in snapshots; redact paths/bodies as elsewhere
- Fail closed on malformed git/compare inputs

## Approval Boundary

**Approved.** Implementation may proceed on `feature/OVA-67-m51-project-overseer`
with rollback `rollback/pre-m51-project-overseer` @ `5d108db`.
