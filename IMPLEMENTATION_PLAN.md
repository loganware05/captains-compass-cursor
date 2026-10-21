# Implementation Plan — Read-Only Persistent Oversight

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `read-only-persistent-oversight` |
| Issue | [#225](https://github.com/loganware05/captains-compass-cursor/issues/225) |
| Notion | [Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.67.0** @ `05dcfba` (#224 merged) |
| Proposed branch | `cursor/225-read-only-persistent-oversight-3ec1` |
| Proposed rollback | `rollback/pre-read-only-persistent-oversight` @ `05dcfba` |
| Proposed release | **v1.68.0** |
| Captain | Logan Ware |
| Created | 2026-10-21 |

## Approval record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR |

## Request

Ship **read-only persistent oversight**: an opt-in composer that runs after a
merge (or on demand) to sync Cognitive Core project-state, take a Project
Overseer snapshot, compare against a prior SHA/snapshot, and draft reconcile
proposals — without auto-applying memory edits or expanding authority.

## Problem Statement

C1 brain sync and M51 Overseer (`status snapshot|explain|compare|reconcile`)
already exist, but operators must invoke them piecemeal. The Oct 20 PDF next
step after E2E is persistent oversight: post-merge drift detection with
**reviewable** reconciliation proposals. Without a single gated surface,
oversight remains ad hoc and easy to skip.

## Desired Outcome

1. New gated surface (defaults):
   - `./scripts/run-oversight.sh` and `northstar oversight run`
   - Optional alias `northstar status post-merge`
2. Composer steps (fail-closed without gates):
   - Require `COMPASS_STATUS_ENABLED=1` (and `COMPASS_BRAIN_ENABLED=1` when
     brain sync is included; `--enable-gates` for hermetic/local convenience)
   - Optional `brain sync` (C1) when brain gate is on
   - `status snapshot` (+ optional explain stub)
   - `status compare --since <sha>` when `--since` provided (else prior snapshot)
   - `status reconcile` → proposal under `.agent/status/reconcile-proposals/`
     with `applied: false`, authority flags false
3. Schema-validated **oversight-run** report under
   `.agent/evidence/read-only-persistent-oversight/` (or
   `.agent/status/oversight-runs/`)
4. Hermetic unit tests; doctor checks; CI offline (stub provider only)
5. Docs: TESTING, handbook note, ADR, CHANGELOG **v1.68.0**

## Acceptance Criteria

- [ ] `oversight run` composes snapshot/compare/reconcile when gated
- [ ] Fail-closed without required enable flags
- [ ] Reconcile proposals never set `applied` / `approved_for_execution` /
      `authority_mutation` true; never rewrite canonical memory
- [ ] Optional brain sync only when `COMPASS_BRAIN_ENABLED=1`
- [ ] Hermetic tests + doctor; evidence recorded
- [ ] Docs/ADR/CHANGELOG; PR after approval (standing order)

## Non-Goals

- Auto-apply reconcile patches or auto-open PRs that rewrite memory
- Background daemon / webhook server required for core path (document hooks as
  optional follow-up)
- Specialized Model Level 0 training
- Expanding Overseer live HTTP provider requirements for CI
- Continuous unsupervised self-training or weight promotion

## Assumptions

1. Existing `orchestrator/status/*` + `orchestrator/cognitive/*` are sufficient
   building blocks; this plan adds a thin composer + report schema.
2. “Post-merge” is operator-triggered CLI first; git hook wiring is optional /
   documented, not a CI hard dependency.
3. Stub StatusProvider remains the hermetic default.

## Open Questions (defaults if approve as written)

1. **Surface name:** `oversight run` + `status post-merge` alias → default **both**.
2. **Git hook:** document optional post-merge hook snippet only (no install by
   default) → default **docs-only hook**.
3. **Brain sync:** include when brain gate on; skip cleanly when off → default **yes**.

## Current-State Analysis

| Asset | Role |
|---|---|
| `orchestrator/status/service.py` | snapshot / explain / compare / reconcile |
| `orchestrator/status/drift.py` | memory drift detectors |
| `orchestrator/status/reconcile.py` | proposal-only drafts (`applied: false`) |
| `orchestrator/cognitive/` | C1 brain sync / freshness |
| Project Overseer Skill | operator procedure for status surfaces |

## Proposed Architecture

```text
northstar oversight run [--since SHA] [--enable-gates]
        │
        ├── require COMPASS_STATUS_ENABLED (+ brain if syncing)
        ├── optional brain sync (C1)
        ├── status snapshot (+ stub explain)
        ├── status compare (since SHA or prior snapshot)
        ├── status reconcile → proposal (applied=false)
        └── write oversight-run report (authority locked false)
```

## Workstreams

| ID | Scope |
|---|---|
| W1 | oversight-run schema + composer service |
| W2 | `run-oversight.sh` + northstar wiring + doctor |
| W3 | Unit tests + hermetic evidence |
| W4 | Docs / ADR / CHANGELOG / optional hook snippet |

## Files Expected to Change

- `orchestrator/oversight/` (new thin module) or `orchestrator/status/post_merge.py`
- `orchestrator/schemas/oversight-run.schema.json` (new)
- `scripts/run-oversight.sh`, `scripts/northstar`, `scripts/doctor.sh`
- `tests/orchestrator/test_read_only_persistent_oversight.py`
- `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md`, handbook
- `docs/plans/READ_ONLY_PERSISTENT_OVERSIGHT.md`
- `.agent/evidence/read-only-persistent-oversight/`

## Testing Strategy

- Unit: fail-closed gates; proposal `applied=false`; authority flags
- Hermetic: full composer on control repo with stub provider
- Regression: existing status/brain tests still pass
- Doctor: schema + script presence + fail-closed

## Security Review

- No secrets in oversight reports (reuse redaction helpers if exporting notes)
- Stub provider only in CI; live HTTP remains Captain-opt-in
- Never auto-apply reconcile or grant execution authority

## Rollback Plan

Tag `rollback/pre-read-only-persistent-oversight` @ `05dcfba`; revert PR.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Scope into auto-apply | Hard non-goal; `applied` const false |
| Hook surprises | Docs-only optional hook; CLI is the product surface |
| Duplicate Overseer paths | Thin compose over existing status/brain APIs |

## Autonomy Budget

| Limit | Value |
|---|---|
| Iterations | 10 |
| Wall time | 6 hours |
| After approval | implement → validate → commit → open PR |

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve read-only-persistent-oversight** (or revise open questions). After
approval, First Mate will branch, implement, validate, **commit, and open the PR**.
Merge remains yours.
