# Implementation Plan — Open UI Control Plane (v1.74.0 proposed)

- Status: **IN PROGRESS**

## Metadata

| Field | Value |
|---|---|
| Status | **IN PROGRESS** |
| Plan ID | `openui-control-plane` |
| Issue | *(placeholder — create after approval)* |
| Baseline | **v1.73.0** @ `6432c23` (#240 merged) |
| Branch | `cursor/openui-control-plane-010c` |
| Rollback | `rollback/pre-openui-control-plane` *(tag after approval)* |
| Proposed release | **v1.74.0** |
| Captain | Logan Ware |
| Created | 2026-10-24 |
| Sources | `NorthStar_Repository_State_2026-10-24.pdf`; `northstar-openui-meta-prompt.md` |

## Approval record

| Field | Value |
|---|---|
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-10-24 |
| Notes | Explicit: “I approve, proceed with Open UI”. Standing order applies. |

---

## Request

Add an on-demand **Open UI** generative control plane so the Captain can approve plans, inspect telemetry, view N2/N3 scorecards, and run closeout reconciliation through streamed interactive widgets — without weakening fail-closed safety hooks or the human authorization boundary.

Also perform the **documentation closeout** called out in the 24 Oct 2026 repository-state assessment (README/PROGRESS/N3 plan drift after #240).

## Problem Statement

1. Captain orchestration today is text-heavy: Cursor slash commands, `./scripts/northstar` CLI, and manual markdown/`IMPLEMENTATION_PLAN.md` inspection. As Skills (47) and specialists (12) scale, approval loops and status checks create cognitive overhead.
2. N1 closeout, N2 `CompassStatusBadge`, and N3 hermetic scorecards already exist as CLI/markdown surfaces; they lack a streaming interactive renderer.
3. Release docs still drift after N3 merge: README shows **1.72.0** while `VERSION` is **1.73.0**; `PROGRESS` still says N3 “PR open”; root plan still labeled N3 **APPROVED** rather than post-merge complete.

## Desired Outcome

1. Control-local Open UI package (`orchestrator/ui/`) using **`@openuidev/react-lang`** + **`@openuidev/lang-core`** (correct current package names; meta-prompt’s `@openui/react` / `@openui/lang` are outdated).
2. System prompt / library schema that constrains models to emit valid **OpenUI Lang** for an allowlisted NorthStar component set.
3. Four widget families (Targets A–D) that stream line-by-line and map to React/Tailwind components:
   - **A** `PlanApprovalCard` — plan summary, risk scorecard, APPROVE / REJECT actions
   - **B** `ControlTowerTelemetry` — 12 agents, Skill ranking, budgets, 7 safety hooks
   - **C** `HermeticScorecard` + `CompassStatusBadge` — N3 metrics + N2 badge
   - **D** `CloseoutLedgerWidget` — SHA compare, evidence matrix, gated closeout triggers
4. Optional `--ui` / `openui-lang` emission from `./scripts/northstar` status/plan/scorecard surfaces; fail closed to markdown/CLI on parse/stream failure.
5. UI approval actions write authenticated Captain approval signals compatible with `plan-approval-check.sh` (`COMPASS_CAPTAIN_APPROVE=1` + committed APPROVED plan) — **never auto-approve**.
6. Docs closeout for v1.73.0 drift + v1.74.0 release notes when Open UI ships.
7. Evidence under `.agent/evidence/openui-control-plane/`.

## Acceptance Criteria

- [x] README / PROGRESS / prior N3 plan closure reconciled to **v1.73.0** / #240 merged (Workstream 0)
- [x] `orchestrator/ui` package builds; depends on `@openuidev/react-lang` and `@openuidev/lang-core` (pinned; supply-chain review recorded)
- [x] OpenUI system prompt / library spec checked in under control paths (e.g. `.cursor/templates/openui-system-prompt.md` + generated `openui.spec.json`)
- [x] Components exist for Targets A–D with accessible labels and keyboard-operable actions
- [x] `northstar … --ui` (or documented equivalent) emits OpenUI Lang for at least: plan approval summary, status/control tower, adaptive scorecard, status closeout
- [x] Invalid OpenUI Lang or stream disconnect → fail closed; markdown/CLI path still works
- [x] UI APPROVE does **not** bypass hooks: requires Captain attestation env + committed plan status; REJECT writes feedback without unlocking implementation
- [x] Doctor + unit/structural tests pass; browser screenshots for widgets recorded
- [x] Security + accessibility reviews recorded; no product-repo pollution (assets stay in `.cursor/`, `orchestrator/`, `scripts/`)
- [x] CHANGELOG / VERSION / ADR for **v1.74.0**; rollback tag documented

## Non-Goals

- N4 multi-repo randomized benchmark (PDF priority 2) — separate plan
- N5 Skill-fit / routing feedback loop (PDF priority 3) — separate plan
- Specialized Model Level 3 / paid GPU training (remains **DEFERRED**)
- Auto-approval, silent Skill/policy promotion, or weakening failClosed hooks
- Shipping Open UI into product application repositories via installer by default
- Requiring Thesys cloud API keys for core hermetic tests (prefer fixture OpenUI Lang streams)

## Assumptions

1. Open UI packages under `@openuidev/*` are acceptable after Captain supply-chain acknowledgment (young ecosystem; Skill `dependency-supply-chain`).
2. First ship is **control-repo / Cursor-adjacent** renderer + CLI emission; full always-on Cursor native chat embedding may be Phase-2 if host APIs are limited.
3. Node.js 20+ is available for `orchestrator/ui` builds in CI or documented optional job.
4. Existing N1/N2/N3 JSON/markdown artifacts are the data source; UI is a presentation + gated action layer, not a new authority store.

## Open Questions (defaults proposed)

| # | Question | Proposed default |
|---|---|---|
| 1 | Package location | `orchestrator/ui/` (control-owned; not installed into product repos by default) |
| 2 | Gate for UI surfaces | `COMPASS_OPENUI_ENABLED=1` or `--ui` with fail-closed when unset for mutating actions |
| 3 | Release version | **v1.74.0** |
| 4 | Hosted Thesys gateway | Optional; hermetic fixtures do not require API keys |
| 5 | Installer packaging | **Do not** copy UI package into product repos in v1; document opt-in later |
| 6 | Workstream 0 (doc closeout) | Include in this PR as prerequisite commits before UI code |

## Current-State Analysis

| Area | Verified state (2026-10-24) |
|---|---|
| Release | `VERSION` **1.73.0**; head `6432c23` (#240); README still **1.72.0** |
| UI package | **None** — no `orchestrator/ui`, no Open UI deps |
| Plan gate | `.cursor/hooks/plan-approval-check.sh` — committed APPROVED + `COMPASS_CAPTAIN_APPROVE=1` |
| Status / closeout | `northstar status …` / `orchestrator/status/` (N1) gated by `COMPASS_STATUS_ENABLED` |
| Adaptive scorecard | `northstar adaptive scorecard` / `orchestrator/adaptive/` (N3) gated |
| Sandbox badge | N2 evidence for `CompassStatusBadge` in `captain-compass-sandbox` only |
| Meta-prompt package names | Outdated (`@openui/*`); use `@openuidev/react-lang`, `@openuidev/lang-core` |

## Proposed Architecture

```
Captain request (/plan-feature --ui | northstar status --ui | …)
        │
        ▼
┌───────────────────┐     OpenUI Lang stream      ┌─────────────────────┐
│ northstar / hooks │ ──────────────────────────► │ @openuidev Renderer │
│ + prompt schema   │                             │ orchestrator/ui     │
└─────────┬─────────┘                             └──────────┬──────────┘
          │                                                  │
          │ markdown fallback (fail-closed)                  │ onAction
          ▼                                                  ▼
   existing CLI / MD                                 approval / closeout
                                                     writers (gated)
```

**Authority:** UI buttons emit *intent*; writers still require Captain attestation and existing gates. Parser errors drop invalid nodes and fall back to non-UI workflow.

### Correct dependency map (vs meta-prompt)

| Meta-prompt name | Actual package |
|---|---|
| `@openui/react` | `@openuidev/react-lang` (+ optional `@openuidev/react-ui`) |
| `@openui/lang` | `@openuidev/lang-core` (`generateSystemPrompt`, parse) |

## Required Capabilities / Reusable Capabilities

From `./scripts/capability-plan.sh --plan-id openui-control-plane` (artifacts under `.agent/plans/openui-control-plane/`):

| Skill (ranked) | Role |
|---|---|
| `react-engineering` | Component library |
| `capability-planning` | Plan sections / manifests |
| `testing-validation` | Doctor + unit + evidence |
| `playwright-browser-validation` | Widget screenshots |
| `accessibility-review` | Keyboard / a11y |
| `dependency-supply-chain` | `@openuidev/*` review |
| `security-review` | Approval bypass / injection |
| `autonomy-budget` | Iteration limits |
| `implementation-planning` | Gate discipline |

**TI candidates:** stub only — **NOT APPROVED FOR EXECUTION**.

## Task Graph

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| `task-ws0-docs` | Reconcile README/PROGRESS/N3 closeout drift | — | no |
| `task-discovery` | Confirm hooks/status/adaptive contracts for UI adapters | task-ws0-docs | no |
| `task-architecture` | Library schema, action contracts, gate design | task-discovery | no |
| `task-impl-frontend` | `orchestrator/ui` + Targets A–D + prompt/spec | task-architecture | yes (per widget) |
| `task-cli-hooks` | `--ui` emitters + fail-closed + approval writers | task-architecture | yes (with frontend) |
| `task-validation` | Doctor, unit, streaming parse tests, a11y, security, screenshots | task-impl-frontend, task-cli-hooks | no |
| `task-documentation` | ADR, CHANGELOG v1.74.0, TESTING, INDEX | task-validation | no |

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| discovery | `repository-scout` | `repository-discovery`, `capability-planning` |
| architecture | `architecture-agent` | `dependency-supply-chain`, `capability-planning` |
| frontend | `implementation-agent` | `react-engineering`, `autonomy-budget` |
| cli/hooks | `implementation-agent` | `security-review`, `testing-validation` |
| validation | `test-engineer` | `testing-validation`, `playwright-browser-validation`, `accessibility-review` |
| documentation | `documentation-agent` | `pull-request-preparation` |

## Workstreams (implementation steps)

### Workstream 0 — Release / memory closeout (from Repository State PDF)

1. Bump README displayed version **1.72.0 → 1.73.0**.
2. Update `PROGRESS.md`: N3 **COMPLETE** / #240 **merged**; clear “PR open”.
3. Archive N3 plan notes into `docs/plans/` / CHANGELOG as needed; leave this file as the active Open UI plan.
4. Capture immutable N3 scorecard path reference under evidence index (no re-run required if artifacts already exist).
5. Exit: docs match `VERSION` 1.73.0 and merged #240.

### Workstream 1 — Environment & system prompt (Phase 1)

1. Scaffold `orchestrator/ui/` (package.json, tsconfig, Vite or tsc).
2. Add pinned `@openuidev/react-lang`, `@openuidev/lang-core`; optional `@openuidev/react-ui` only if primitives are reused.
3. Record supply-chain review under `.agent/evidence/openui-control-plane/SUPPLY_CHAIN.md`.
4. Author `.cursor/templates/openui-system-prompt.md` + generate `openui.spec.json` from the component library.
5. Document: models must emit OpenUI Lang for allowlisted components only.
6. Exit: `npm test` / typecheck green on empty library + prompt generation smoke.

### Workstream 2 — React component library (Phase 2 / Targets A–D)

1. `PlanApprovalCard.tsx` — summary drawers, risk badges (files, hooks, specialists), APPROVE / REJECT.
2. `ControlTowerTelemetry.tsx` — agent grid, Skill matrix, budget bars, hook status grid.
3. `HermeticScorecard.tsx` — 7-metric baseline vs evidence-informed chart; Level 3 deferral card.
4. `CompassStatusBadge.tsx` — control-local mirror of N2 badge pattern (not product-repo code).
5. `CloseoutLedgerWidget.tsx` — SHA side-by-side, evidence matrix, gated closeout/cleanup actions.
6. Register all in `createLibrary({ root, components })`.
7. Exit: Story/fixture render of each widget from static OpenUI Lang fixtures.

### Workstream 3 — CLI & hooks integration (Phase 3)

1. Extend `scripts/northstar` / relevant `run-*.sh` to accept `--ui` and emit fenced OpenUI Lang (or write `.agent/ui/*.openui`).
2. Adapters:
   - Plan summary ← `IMPLEMENTATION_PLAN.md` / capability-plan artifacts
   - Control tower ← status snapshot + budget files + hook inventory
   - Scorecard ← `orchestrator.adaptive` JSON
   - Closeout ← `status closeout` JSON
3. Approval writer: UI APPROVE sets plan status only when `COMPASS_CAPTAIN_APPROVE=1` and subsequent commit satisfies `plan-approval-check.sh`; otherwise deny with clear message.
4. Reject path: append feedback to plan / `.agent/sessions/` without unlocking product edits.
5. Fail-closed: missing gate, parse error, or disconnect → non-zero advisory + markdown path.
6. Exit: hermetic tests prove approve blocked without attestation; markdown path unchanged when `--ui` absent.

### Workstream 4 — Validation & release (Phase 4)

1. `./scripts/doctor.sh`, `./tests/run.sh`, orchestrator unit tests for emitters/parsers.
2. Structural examples under `examples/structural-tests/` if applicable.
3. Playwright/browser screenshots for A–D → `.agent/evidence/openui-control-plane/`.
4. Security review (approval bypass, XSS via streamed props, path writes).
5. Accessibility review (focus order, names, contrast).
6. VERSION **1.74.0**, ADR-094, CHANGELOG, TESTING, docs/INDEX.
7. Rollback tag `rollback/pre-openui-control-plane` at pre-change SHA.
8. Exit: Definition of Done checklist complete; First Mate inspection notes in evidence.

## Files Expected to Change (post-approval)

| Path | Change |
|---|---|
| `README.md`, `PROGRESS.md` | WS0 version/status reconciliation |
| `orchestrator/ui/**` | New Open UI package + components |
| `.cursor/templates/openui-system-prompt.md` | Prompt schema |
| `scripts/northstar`, `scripts/run-status.sh`, related | `--ui` emission |
| `orchestrator/status/`, `orchestrator/adaptive/` | Thin OpenUI serializers (optional) |
| `.cursor/hooks/plan-approval-check.sh` | Only if needed for UI attestation compatibility (prefer no weaken) |
| `tests/orchestrator/test_openui_*.py`, UI unit tests | Coverage |
| `docs/plans/OPENUI_CONTROL_PLANE.md`, `DECISIONS.md`, `CHANGELOG.md`, `VERSION`, `TESTING.md` | Memory + release |
| `.agent/evidence/openui-control-plane/**`, `.agent/budgets/openui-control-plane.md` | Evidence + budget |

## Testing Strategy

| Layer | Command / artifact |
|---|---|
| Doctor | `./scripts/doctor.sh` |
| Unit | `./tests/run.sh`; UI package test script; OpenUI Lang fixture parse |
| Integration | `northstar status --ui`, `adaptive scorecard --ui` with gates + fixtures |
| E2E / browser | Playwright screenshots of A–D |
| Security | `.agent/evidence/openui-control-plane/SECURITY.md` |
| Accessibility | `.agent/evidence/openui-control-plane/ACCESSIBILITY.md` |
| Rollback review | Documented tag + revert instructions |

## Security Notes

- No secrets in prompts, fixtures, or evidence.
- UI actions are not authority: hooks remain fail-closed.
- Sanitize/allowlist component props; do not `eval` streamed content.
- Young `@openuidev/*` packages require Captain supply-chain acknowledgment before pin.
- Do not install UI runtime into product repos by default.

## Accessibility Review

Required for all interactive widgets: keyboard activation for APPROVE/REJECT, visible focus, sufficient contrast, accessible names for telemetry grids and charts.

## Migration Plan

- Additive feature behind `--ui` / `COMPASS_OPENUI_ENABLED`.
- Existing CLI/markdown workflows remain default.
- No product-repo installer migration in v1.74.0.

## Deployment Plan

- Control-repo merge + release tag **v1.74.0**.
- Optional local `orchestrator/ui` build in CI (or documented manual build).
- No cloud deploy target (control template repo).

## Rollback Plan

1. Revert merge commit or reset to `rollback/pre-openui-control-plane`.
2. Operators omit `--ui`; markdown/CLI unchanged.
3. Remove `orchestrator/ui` node_modules if present (not committed).

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Meta-prompt wrong package names | Use `@openuidev/*`; verify against openui.com docs at implement time |
| Cursor chat cannot host React Renderer | Ship CLI/file emission + local renderer first; document Cursor embedding as follow-up |
| Approval UI bypass attempt | Reuse plan-approval-check; deny without `COMPASS_CAPTAIN_APPROVE` |
| Parser partial UI | Fail closed to markdown; never treat partial approve as success |
| Scope creep into N4/N5 | Explicit non-goals; separate plans |

## Evaluation Strategy

- Fixture OpenUI Lang streams parse without orphaned critical roots.
- Approve/reject contract tests vs hook behavior.
- No regression in doctor/hooks/adaptive/status gates.
- Adversarial review before merge.

## Learning Plan

Retain under `.agent/plans/openui-control-plane/` and evidence folder; feed Experience only after Captain-reviewed runs (proposal-only routing).

## Autonomy Budget

| Limit | Value |
|---|---|
| Maximum iterations | 8 |
| Maximum failed validation cycles | 3 |
| Maximum estimated cost | Low (no paid GPU; optional npm only) |
| Maximum elapsed wall time | Stop and report if blocked on Cursor host UI APIs |
| Budget ledger | `.agent/budgets/openui-control-plane.md` *(create after approval)* |
| On limit | `.agent/evidence/openui-control-plane/BUDGET_STOP_REPORT.md` |

## Definition of Done

- All Acceptance Criteria checked
- Evidence matrix satisfied for UI + control-script change
- Security + accessibility evidence present
- Docs/VERSION/CHANGELOG updated
- Rollback tag exists
- First Mate inspected final result
- Plan status → **COMPLETE** only after merge

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Say **approve** / **proceed with Open UI** (or equivalent) to unlock Workstreams 0–4.  
Machine-generated capability matches are proposals only.

## Related follow-ups (out of scope)

From Repository State PDF — track separately after this plan:

1. **N4 benchmark** — randomized baseline vs evidence-informed across independent stacks  
2. **N5 feedback** — validate Skill-fit/routing proposals from N4 (no auto-promotion)  
3. **Model proof** — small-adapter vs retrieval/hosted baselines (separate cost approval)  
4. **Conditional Level 3** — only after demonstrated benefit
