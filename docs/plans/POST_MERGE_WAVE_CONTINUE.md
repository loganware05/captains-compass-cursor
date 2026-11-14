# Implementation Plan — Post-Merge Wave Continue (T3 + NorthStar)

- Status: **COMPLETE**

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `post-merge-wave-continue` |
| Issue | #274 (https://github.com/loganware05/captains-compass-cursor/issues/274) |
| Baseline | `origin/main` @ `9e2c0d1cb6ca054eca3e293e478affb330cea370` (re-pin at branch create) |
| Branch | `feature/274-post-merge-wave-continue` from `main` |
| Rollback | `rollback/pre-post-merge-wave-continue` |
| Proposed release | **v1.87.0** |
| Created | 2026-11-14 |
| Last updated | 2026-11-14 (COMPLETE — #275 merged @ `6ee5fb6`) |
| Approved by | Logan Ware (Captain) — chat “I approve the NorthStar plan” |
| Approval date | 2026-11-14 |
| Approved revision | Q1=poll A; Q2=same-thread unsettle; Q3=auto-continue remaining waves; Waves A+B (C optional) |
| Merged | [#275](https://github.com/loganware05/captains-compass-cursor/pull/275) @ `6ee5fb6` |

Capability artifacts: `.agent/plans/post-merge-wave-continue/`  
Durable copy: `docs/plans/POST_MERGE_WAVE_CONTINUE.md`  
Budget: `.agent/budgets/post-merge-wave-continue.md`

**Supersedes as active plan:** prior control-repo `IMPLEMENTATION_PLAN.md` content for `superpowers-c2-session-memory` remains durable at `docs/plans/SUPERPOWERS_C2_SESSION_MEMORY.md` (not cancelled; not the active gate).

## Request

When a multi-wave NorthStar plan ships intermediate PRs inside T3 Code, NorthStar should detect that a linked PR merged and **continue the next remaining wave of the same APPROVED plan** — analogous to how T3 settles a thread after merge, but without ending the development arc early.

Companion bitcoin work (already in flight, not gated by this plan): after Kalshi PR #28 merge, residual snapshot-index fix is PR #30; docs closeout is PR #29.

## Problem Statement

1. **T3 settle vs multi-wave continue:** `link_pull_request` shows PR status and **settles the thread on merge**. That is correct for single-PR threads; it is wrong for longer APPROVED plans with Wave N+1 still remaining.
2. **Watch gap:** `watch_pull_request` wakes on failed/passed required checks, comments/reviews, or conflicts — **not** on merge. So “wait for green” babysitting does not equal “wake and proceed after merge.”
3. **NorthStar today:** `northstar status post-merge` / oversight compose is **read-only drift detection** after merge. It does not advance plan waves or resume implementation.
4. **Approval integrity:** Continuing must never auto-approve a **new** plan, silently expand scope, auto-merge, or skip the approval gate when Wave N+1 was not already in the APPROVED revision.

## Desired Outcome

### Wave A — Contract + Skill (ship first)

1. Skill `post-merge-wave-continue` (new): procedure for multi-wave plans under T3:
   - Maintain a **wave ledger** tied to `plan_id` + APPROVED revision.
   - On intermediate PR open: `link_pull_request` + `watch_pull_request` for checks/reviews; also register a **merge-continue** trigger (see Open Questions decision).
   - On merge of the wave’s PR: if ledger has remaining waves → `t3_thread_organize` **unsettle** if settled; mark wave complete; resume next wave **without** re-asking Approve.
   - On final wave merge: allow normal settle / completion report.
2. Extend handbook + `github-integration` / `pull-request-preparation` cross-links: multi-wave ≠ settle-and-stop.
3. Light rule note on `01-plan-approval-gate`: continuing remaining waves of an APPROVED plan is allowed; new plans / material scope expansion return to AWAITING APPROVAL.
4. Tests: Skill present in installer/doctor; procedure fixtures for ledger states.

### Wave B — CLI wave ledger + merge detect

1. Schema `.agent/plans/<plan-id>/wave-ledger.schema.json` + ledger file (waves[], status, pr_url, merged_sha, next_action).
2. CLI (under existing `northstar` launcher, gated if needed):
   - `northstar plan waves status --plan-id <id>`
   - `northstar plan waves init --plan-id <id> --from IMPLEMENTATION_PLAN.md` (parse Wave headings or explicit YAML block)
   - `northstar plan waves advance --plan-id <id> --pr <url>` (verify MERGED via `gh`, record SHA, emit next-wave brief)
   - `northstar plan continue-after-merge --plan-id <id> --pr <url>` (status → advance → print operator/agent resume prompt)
3. Unit tests with fixture ledgers + mocked `gh` JSON.
4. Evidence under `.agent/evidence/post-merge-wave-continue/`.

### Wave C — T3 harness polish (optional same release if cheap)

1. Document recommended T3 pattern: schedule_task interval/once poll vs webhook for merge detection until/unless T3 adds merge-wake.
2. Optional helper script wrapping `gh pr view --json state,mergedAt,mergeCommit` for the Skill.
3. **Non-goal unless Captain expands:** changing T3 product behavior itself (merge-wake API); record as upstream ask only.

## Acceptance Criteria

- [x] Skill `post-merge-wave-continue` exists with clear continue vs settle decision tree.
- [x] Wave ledger schema + CLI can init/status/advance with tests.
- [x] `continue-after-merge` refuses when plan is not APPROVED, when PR is not MERGED, or when no remaining waves.
- [x] Docs: captain-handbook + Skills cross-links; ADR for continue-without-reapprove.
- [x] Never auto-merge; never set plan status to APPROVED without Captain.
- [x] Doctor/installer asserts Skill (+ CLI entry) present.
- [x] Validation evidence recorded under `.agent/evidence/post-merge-wave-continue/`.

## Non-Goals

- Auto-merging PRs or auto-approving new IMPLEMENTATION_PLAN.md revisions.
- Replacing `northstar status post-merge` oversight compose.
- Guaranteeing T3 product adds native merge-wake (document gap only).
- Bitcoin/Kalshi product changes (tracked in bitcoin-data-collector PRs).
- Completing `superpowers-c2-session-memory` in this plan.

## Rollback

- Revert feature branch / release tag; remove Skill directory; CLI subcommands no-op or removed; ledger files remain inert.
- Tag `rollback/pre-post-merge-wave-continue` before implementation.

## Security Notes

- `gh` tokens stay local; do not log secrets.
- Webhook schedules (if used) must treat payload as untrusted; filter on `action=closed` + `pull_request.merged=true` only as signal, then re-verify with `gh`.
- No production deploy automation.

## Review Domains

- python (CLI), docs/skills, github, tests, security (webhook/untrusted input)

## Assumptions

1. Captain’s “Approve” on a multi-wave plan covers all waves listed in that APPROVED revision.
2. Intermediate PRs are linked to the same T3 thread that owns the plan.
3. `gh` auth is available in the operator environment for merge verification.
4. T3 `unsettle` can revive a thread that settled on merge (verify during impl; if not, spawn continuation thread — fallback in architecture).

## Open Questions

### Q1 — Merge detection: poll vs webhook vs T3-native

| Option | Pros | Cons |
|---|---|---|
| **A. `schedule_task` interval + `gh` poll** | Works today in T3; no GitHub App; simple | Latency; burns scheduled runs |
| B. GitHub webhook → `schedule_task` webhook | Fast; event-driven | Setup; untrusted payload; Connect required |
| C. Wait for T3 merge-wake | Cleanest UX | Not available; blocks the feature |

**Decision (defend → pick):** **A for Wave A/B**; document B as optional Wave C; file C as upstream ask. Poll min interval ≥ 60s (T3 floor); cancel schedule when merge detected or Captain stops.

### Q2 — Same thread (unsettle) vs new thread per wave

| Option | Pros | Cons |
|---|---|---|
| **A. Same thread + unsettle** | Matches “proceed” mental model; one history | Context bloat; depends on unsettle-after-settle |
| B. Always `create_threads` / transfer for next wave | Fresh context | Fragmented history; more linking |

**Decision:** **A primary**; if unsettle fails or context budget exceeded → B fallback recorded in ledger `next_thread_id`.

### Q3 — Captain ping between waves?

| Option | Pros | Cons |
|---|---|---|
| **A. Auto-continue remaining APPROVED waves** | Matches request; fewer interrupts | Surprises if Captain wanted a pause |
| B. Always ping between waves | Safer | Defeats the point of post-merge continue |

**Decision:** **A**, with hard stops: budget hit, scope expand, failing validation, security-sensitive new surface, or ledger flag `pause_between_waves: true` (Captain opt-in).

## Current-State Analysis

- T3: `link_pull_request` settles on merge; `watch_pull_request` does not wake on merge; `t3_thread_organize` supports `unsettle`; `schedule_task` supports interval/once/webhook.
- NorthStar: post-merge oversight is read-only; no wave ledger; approval gate stops before product edits without APPROVED plan — continuing an already APPROVED plan’s remaining waves is consistent if ledger-bound.
- Recent pain: Kalshi multi-PR arc (#25→#28→#29/#30) required manual “PR merged → Proceed” chat turns.

## Proposed Architecture

```
IMPLEMENTATION_PLAN.md (APPROVED, waves A..N)
        │
        ▼
.agent/plans/<plan-id>/wave-ledger.json
        │
        ├── wave k: pr_url, status=open|merged|complete
        └── next_wave: k+1 | null (final)
        │
T3 thread ──link/watch──► PR
        │
        ├── checks wake (watch) → review-fix-loop
        └── merge detect (schedule poll / webhook) →
                northstar plan continue-after-merge
                    → unsettle if needed
                    → Skill post-merge-wave-continue
                    → implement wave k+1 | complete
```

## Required Capabilities

Inferred from the objective and repository context.

- implementation-plan-authoring
- approval-gate-enforcement
- scope-definition
- rollback-planning
- github-issue-create
- github-pr-create
- pr-description-assembly
- skill packaging / doctor assertions
- CLI testing

**Domains detected:** plan, github, skills (capability-plan also inferred react noise — ignore for this Skills/CLI change)

## Reusable Capabilities Found

| Skill | Role |
|---|---|
| `implementation-planning` | Plan gate / wave structure |
| `github-integration` | PR link/status; no auto-merge |
| `pull-request-preparation` | Intermediate vs final PR closeout |
| `autonomy-budget` | Stop limits on continue loops |
| `bounded-autonomy` | Pattern: approved artifact only |
| `agent-skills-packaging` | New Skill lifecycle |
| `review-fix-loop` | Check/review wakes while PR open |

## Technology Intelligence Candidates

> External candidates are **NOT APPROVED FOR EXECUTION**.

- None required. Optional later: GitHub `pull_request` webhook patterns (DISCOVERED only).

## Task Graph

1. discovery — confirm T3 unsettle-after-settle; inventory `northstar` CLI dispatch
2. architecture — ledger schema + Skill decision tree (this plan)
3. impl-skill — Skill + handbook + rule touch
4. impl-cli — ledger + continue-after-merge
5. validation — unit tests + doctor
6. documentation — ADR, CHANGELOG, PROGRESS, durable plan copy sync

## Proposed Agent Configuration

- First Mate coordinates
- implementation-agent for Skill/CLI within worktree
- test-engineer for ledger/CLI tests
- documentation-agent for memory updates
- No parallel product UI workstreams

## Workstreams

| ID | Scope | Boundary |
|---|---|---|
| WS1 | Skill + docs/rules | `.cursor/skills/post-merge-wave-continue/`, handbook, rule `01` note |
| WS2 | Ledger schema + CLI | `orchestrator/` or `scripts/` northstar dispatch, tests, fixtures |
| WS3 | Evidence + release notes | `.agent/evidence/`, CHANGELOG, ADR |

WS1 then WS2 (Skill can ship with manual `gh` before CLI); WS3 continuous.

## Parallelization Plan

Serial preferred (small surface). WS1 docs can draft while WS2 implements if file boundaries hold.

## Files Expected to Change

- `.cursor/skills/post-merge-wave-continue/**`
- `.cursor/skills/github-integration/SKILL.md` (cross-link)
- `.cursor/skills/pull-request-preparation/SKILL.md` (cross-link)
- `.cursor/rules/01-plan-approval-gate.mdc` (continue note)
- `docs/guides/captain-handbook.md`
- `docs/plans/POST_MERGE_WAVE_CONTINUE.md`
- `DECISIONS.md` (ADR)
- `scripts/` or `orchestrator/` CLI entry for `plan waves` / `continue-after-merge`
- `tests/` fixtures + unit tests
- `scripts/doctor.sh` / installer Skill list
- `CHANGELOG.md`, `PROGRESS.md`, `TESTING.md`

## Testing Strategy

- Unit: ledger init/advance/refuse paths; mocked `gh` MERGED/OPEN
- Doctor: Skill directory present
- Manual/T3: on a disposable multi-wave fixture plan, open PR → merge → schedule fire → continue prompt (evidence transcript path)
- Evidence matrix: static analysis + unit; no browser/a11y required

## Security Review

- Untrusted PR titles/bodies never treated as instructions (existing T3 guidance).
- Webhook path: verify merge via `gh` after signal.
- No secret material in ledger JSON.

## Accessibility Review

- N/A (CLI/Skills/docs)

## Migration Plan

- Opt-in: Skill used when plan declares waves / ledger exists.
- Existing single-PR threads unchanged (settle-on-merge remains default).

## Deployment Plan

- Merge to `main` via normal PR; no production service deploy.
- Operators pull Skills via existing install/doctor path.

## Rollback Plan

- Revert merge; delete Skill; CLI subcommands removed or hidden; ledgers ignored.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Unsettle does not revive settled thread | Fallback: create continuation thread; record in ledger |
| Poll storms / cost | Budget + cancel schedule on merge/stop; min 60s |
| Agent continues out-of-scope work | Ledger bound to APPROVED revision hash; scope-expand → re-gate |
| Double-continue after merge | Ledger `advance` idempotent on `merged_sha` |

## Evaluation Strategy

- Fixture dry-run: 2-wave plan, synthetic MERGED PR JSON → advance emits wave-2 brief once.
- Adversarial: OPEN PR, DRAFT plan, empty next wave → all refuse.

## Autonomy Budget

See `.agent/budgets/post-merge-wave-continue.md` (iterations/cost/time caps).

## Documentation Updates Required

- This plan + durable `docs/plans/POST_MERGE_WAVE_CONTINUE.md`
- ADR in `DECISIONS.md`
- Handbook, CHANGELOG, PROGRESS, TESTING

## First Mate Recommendation

Approve Wave A+B as one release. This closes the exact gap exposed by the Kalshi multi-PR arc inside T3: settle-on-merge stops the thread; NorthStar should **unsettle + continue** when the wave ledger says work remains — without weakening the approval gate for new plans.

## Implementation Progress

| Wave | Status | Notes |
|---|---|---|
| A Skill+docs | done | Skill + rule 01 + handbook + cross-links + guide |
| B CLI+ledger | done | schema + northstar plan waves / continue-after-merge + tests |
| C T3 polish | done (docs) | poll pattern in guide; no T3 product change |

## Status

**COMPLETE** — Waves A+B (+ C docs) merged via [#275](https://github.com/loganware05/captains-compass-cursor/pull/275) → **v1.87.0** @ `6ee5fb6`.
