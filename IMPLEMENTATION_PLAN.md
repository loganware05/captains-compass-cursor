# Implementation Plan — B4 Supervised FIX→SUBMIT

- Status: **COMPLETE**

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain |
| Approved at | 2026-11-25 |
| Defaults | Q1=yes → v1.95.0; Q2=hermetic/sandbox; Q3=evidence-only + optional draft flag off; Q4=defer live XRV/#237/Bend var |
| Issue | [#313](https://github.com/loganware05/captains-compass-cursor/issues/313) |
| Rollback | `rollback/pre-b4-fix-submit-supervised` @ `59a149a` |
| Branch | `feature/313-b4-fix-submit-supervised` |
| Worktree | `/Users/loganware/Documents/Personal/Code/captains-compass-b4-fix-submit` |


## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `b4-fix-submit-supervised` |
| Issue | [#313](https://github.com/loganware05/captains-compass-cursor/issues/313) |
| Proposed release | **v1.95.0** |
| Baseline | `origin/main` @ `59a149a` / **v1.94.0** (closeout [#312](https://github.com/loganware05/captains-compass-cursor/pull/312) merged) |
| Rollback | `rollback/pre-b4-fix-submit-supervised` @ `59a149a` |
| Prior | B4 packet MVP shipped **v1.35.0**; FIX/SUBMIT still prepare-only |

Budget: `.agent/budgets/b4-fix-submit-supervised.md`  
Durable copy: `docs/plans/B4_FIX_SUBMIT_SUPERVISED.md`

## Goal

Close the B4 gap after packet MVP: hermetic/sandbox-supervised **FIX→TEST→SUBMIT** that can prepare a **draft PR** on an allowlisted repo when Captain authorizes — **never auto-merge**, no live product FIX without utterance.

## Why this pick (scaffolding↑ / ops↓ / blast↓)

- XRV hermetic ops-verified just closed (#310 / v1.94.0); live deploy still deferred
- #237 Level 3 remains paused (no paid GPU)
- Bend CI var is ops-only (Captain can flip without a code plan)
- B4 packet exists; SUBMIT is still metadata-only — highest leverage bounded product gap

## In scope

1. Extend `orchestrator/repair` + CLI for supervised FIX authorization → evidence + optional draft-PR submit helper (allowlist + Captain utterance gate)
2. Hermetic fixture path (sandbox report) proving FIND→PROVE→packet→fix_authorized→submit_prepared
3. Hard locks: `never_auto_merge`, allowlisted repos only, no silent authority mutation
4. Docs / doctor / tests / VERSION **v1.95.0**

## Out of scope

- Auto-merge or auto-close issues
- Unallowlisted / production product FIX without Captain
- XRV live deploy drill
- Specialized Level 3 (#237)
- Enabling `COMPASS_BEND_STRICT_LAWS_CI` (Captain ops)

## Acceptance criteria

- [x] Authorized repair run reaches `submit_prepared` (or equivalent) with draft-PR helper evidence
- [x] Unauthorized path cannot submit
- [x] Hermetic unit/integration tests green; doctor green
- [x] Locks remain false for auto-merge / auto-promote

## Open questions (defaults on Approve)

1. **Proceed with `b4-fix-submit-supervised` → v1.95.0?** Default: **yes**
2. **Hermetic/sandbox only (no live product FIX)?** Default: **yes**
3. **Draft PR via `gh` when authorized, or evidence-only submit prep?** Default: **evidence-only + optional `--open-draft-pr` flag (off by default)**
4. **Defer XRV live / #237 / Bend CI var?** Default: **yes**

## Approval Boundary

**Approved.** Implementation in progress under autonomy budget .


## Completion

| Field | Value |
|---|---|
| Completed at | 2026-11-25 |
| Proposed version | **v1.95.0** |
| Validation | `test_m32_b4_repair_loop` + doctor + hermetic demo `submit_prepared` |
| Live FIX / draft execute | Deferred (hermetic + execute gate) |
