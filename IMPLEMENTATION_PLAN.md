# Implementation Plan — M22/M23 NorthStar live ops + TI skill flywheel

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED — M23 IMPLEMENTATION COMPLETE (pending merge/tag)** |
| Plan ID | `m22-m23-northstar-ops-ti-flywheel` |
| Supersedes | `issue-50-northstar-m4-bridge` (CLOSED — shipped as v1.26.0) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.27.0` on `main` (M22 shipped) |
| Prepared | 2026-09-09 |
| Start gate | Open — Captain approved 2026-09-09; M23 start directed after #129 + sandbox#43 |
| Branch | `cursor/m23-ti-skill-flywheel-6044` (M23); M22 was `cursor/m22-northstar-unattended-ops-6044` |
| M22 | [#129](https://github.com/loganware05/captains-compass-cursor/pull/129) + sandbox [#43](https://github.com/loganware05/captain-compass-sandbox/pull/43) merged |
| M23 PR | [#130](https://github.com/loganware05/captains-compass-cursor/pull/130) |
| Target releases | **v1.27.0** (M22 — shipped), **v1.28.0** (M23) |
| Product target | `loganware05/captain-compass-sandbox` **only** |
| Rollback tags | `rollback/pre-m22-northstar-ops`, `rollback/pre-m23-ti-flywheel` |

## Request (Captain-level)

With M21 / #50 complete, begin using the full coordinated operating routine across
GitHub, Linear, Slack, and Cursor — starting with **unattended** bots/webhooks —
while continuing product work in the sandbox. In parallel, improve NorthStar Skills
via GitHub Stars categorization and sandbox learning, including deeper
security/supply-chain judgment and fixed usefulness labels before any Skill draft
(example intent: starred design repos such as `pbakaus/impeccable` → categorize →
secure → usefulness labels → sandbox UI experiments → Captain-gated Skill promotion).

## Captain decisions (locked)

1. **Connector order:** GitHub + Linear first; then Slack intake/notify.
2. **Runtime:** Unattended webhooks/bots (not Captain-local sessions only).
3. **Product scope:** Sandbox only for these milestones.
4. **TI entry:** External repos **must be starred** to enter Technology Intelligence.
5. **Skill draft gate:** Deeper dependency/supply-chain review **before** any Skill draft.
6. **Usefulness:** Fixed labels (e.g. `frontend-ui`, `design-system`, …).
7. **Sandbox learning:** Bounded UI experiments inside `captain-compass-sandbox`.
8. **Cadence:** Two milestones (M22 then M23).

## Problem statement

1. NorthStar connected routine is **fixture-proven** but does not yet run live
   unattended Slack/Linear/GitHub/Cursor traffic behind
   `scripts/run-northstar-routine.sh`.
2. There is **no webhook/bot ingress** today — only fixture adapters + CLI.
3. Stars TI can categorize starred repos, but lacks a first-class
   **security + supply-chain + usefulness-label** scorecard before Skill drafts.
4. Skill learning loop can propose improvements, but does not yet enforce the
   deeper gates above, and does not drive bounded sandbox UI experiments as
   evidence for design-oriented Skills.

## Current-state summary

| Surface | Today |
|---|---|
| Routine | `orchestrator/integrations/` + fixture adapters; ADR-037/038 |
| Approval | GitHub + plan digest only (fail-closed) |
| Linear / Slack | Fixture ledger / notify; never approval |
| TI Stars | Live/fixture categorize; labels: `frontend-ui`, `backend-library`, `devtool`, `ml-data`, `other` |
| Learning | M19/M20 loop + Captain-gated apply; sandbox harness does not clone external repos |
| Sandbox | Vite React app; refresh through Compass 1.26.0 |

## Desired outcomes

### M22 — NorthStar Unattended Connected Ops → **v1.27.0**

Unattended GitHub + Linear (then Slack notify/intake) feed the existing NorthStar
routine without weakening fail-closed approval. Sandbox is the only product
dispatch/allowlist target.

### M23 — TI Scorecard + Skill Flywheel → **v1.28.0**

Starred-only TI → fixed usefulness labels → mandatory security + supply-chain
evidence → Skill drafts → bounded sandbox UI experiments → Captain-gated
Skill/procedure promotion.

## Acceptance criteria

### M22 (v1.27.0)

- [ ] Unattended ingress (webhook/bot worker) accepts GitHub deliveries with
      signature verification + idempotent `delivery_id` handling.
- [ ] Live GitHub path advances/records Captain approval via plan digest only;
      missing/invalid approval fail-closes (`AWAITING_CAPTAIN_APPROVAL` / stop).
- [ ] Live Linear ledger create/update/link works; Linear **cannot** approve or
      dispatch.
- [ ] Slack notify (and intake if capacity) ships **after** GitHub+Linear health;
      Slack **cannot** approve or dispatch.
- [ ] Fixture mode remains CI default; live mode requires explicit Captain-gated
      config/secrets (never committed).
- [ ] Cursor agent identity pin preserved (`BLOCKED_AGENT_IDENTITY` on mismatch)
      unless Captain revises via ADR.
- [ ] No auto-merge, auto-release, live Skill install, or weight auto-apply.
- [ ] Secrets redacted in logs/events/evidence; doctor + docs updated for live ops.
- [ ] `docs/SANDBOX_VALIDATION.md` row for Compass **1.27.0**; sandbox refresh PR.
- [ ] Tests: fixture suite green; live paths covered with injected doubles (no
      live credentials in CI).
- [ ] Tag/release **v1.27.0** + rollback tag `rollback/pre-m22-northstar-ops`.

### M23 (v1.28.0)

- [x] Fixed usefulness/category label set extended at least with **`design-system`**
      (and any Captain-confirmed additions) in `DEFAULT_CATEGORIES`, manual labels,
      docs, and tests.
- [x] TI paths enforce **starred provenance** for external repo entry (reject
      non-starred feeds).
- [x] Before any Skill draft: required **security-review** +
      **dependency-supply-chain** evidence artifacts; fail closed if missing.
- [x] `skill-learning-loop` / `apply-skill-improvement` document and enforce the
      new gates; live apply remains `--captain-approved` only.
- [x] At least one **bounded UI experiment** lands only in
      `captain-compass-sandbox` with Playwright/a11y evidence linked from control
      validation docs.
- [x] Example path supported for a **starred** design repo (e.g. impeccable once
      starred): categorize → scorecard → draft proposal (no auto Skill install).
- [x] `approved_for_execution` stays false for TI candidates; no clone/exec of
      starred repos from learning/TI.
- [x] Sandbox refresh + smoke gate for **1.28.0** (branch
      `cursor/refresh-compass-1.28.0-6044`; PR pending parent).
- [ ] Tag/release **v1.28.0** + rollback tag `rollback/pre-m23-ti-flywheel`.

## Non-goals

- Moving approval authority to Slack, Linear, or Notion
- Auto-merge / auto-release / unattended live Skill install
- Installing Compass into non-sandbox product repos in these milestones
- Arbitrary non-starred URL ingest into TI
- Cloning or executing third-party repos inside the control learning loop
- Reopening closed #50 / v1.26.0 scope
- Multi-tenant hosted SaaS control plane

## Proposed architecture

```text
M22:
  GitHub webhook/bot ──► ingress (verify + idempotency)
  Linear API/bot     ──► ledger mirror
  Slack bot (later)  ──► intake/notify
         │
         ▼
  NorthStar routine (existing state machine)
         │
         ├─ Captain approval: GitHub + plan digest ONLY
         └─ Cursor execution: pinned agent, sandbox allowlist

M23:
  Starred repos ──► TI categorize (fixed labels)
                 ──► security-review + supply-chain evidence
                 ──► usefulness labels / scorecard
                 ──► skill-learning-loop drafts (staging)
                 ──► bounded sandbox UI experiment evidence
                 ──► Captain-gated Skill apply / PR
```

### Implementation surfaces (proposed)

**M22**
- New ingress worker/receiver (greenfield) feeding
  `orchestrator/integrations/events.py` + routine
- Live adapter modes beside fixtures for GitHub / Linear / Slack
- Secrets via environment / secret store (never committed)
- Docs: `docs/integrations/{github,linear,slack}.md`, Skill
  `northstar-connected-routine`

**M23**
- Extend `DEFAULT_CATEGORIES` + manual labels (+ `design-system`)
- Scorecard artifact schema + promote/learning gates
- Wire `security-review` + `dependency-supply-chain` before draft write
- Sandbox UI experiment + `docs/SANDBOX_VALIDATION.md` / checklist attachment
- Example scorecard evidence for one starred design-oriented repo

## Workstreams

| ID | Milestone | Scope |
|---|---|---|
| W22A | M22 | Ingress design (hosting choice, signatures, allowlists) |
| W22B | M22 | Live GitHub adapter + approval verify |
| W22C | M22 | Live Linear ledger |
| W22D | M22 | Slack notify/intake after GH+Linear |
| W22E | M22 | Docs, doctor, CI fixtures, sandbox refresh, release |
| W23A | M23 | Label taxonomy (`design-system`, …) |
| W23B | M23 | Starred-only TI enforcement |
| W23C | M23 | Security + supply-chain gate before Skill draft |
| W23D | M23 | Learning-loop / apply-improvement alignment |
| W23E | M23 | Bounded sandbox UI experiment + validation/release |

## Safety and authority

- GitHub + plan digest remain the sole engineering approval authority (ADR-037).
- Slack / Linear / Notion are never approval or dispatch authorities.
- No auto-merge, auto-release, or unattended live Skill install.
- Secrets never enter prompts, logs, Slack, Linear, GitHub mirrors, or fixtures.
- TI candidates remain non-executable (`approved_for_execution: false`); no
  third-party clone/exec from TI/learning.
- Wrong Cursor agent → fail closed.
- Sandbox-only product target for M22/M23.
- Routing weight apply and live Skill apply remain explicit Captain gates.

## Autonomy budget (activates only after plan approval)

| Limit | Value |
|---|---|
| Maximum iterations per milestone | 8 |
| Maximum failed validation cycles | 3 |
| Live credential usage in CI | 0 (doubles/fixtures only) |
| Weight-apply / live Skill apply without Captain flag | 0 |
| Stop on scope change / destructive / unresolved security high | true |

## Defaults for remaining choices (override on approval if desired)

| Topic | Default if Captain silent |
|---|---|
| Ingress hosting | GitHub App / webhook receiver as smallest always-on worker (Captain picks host) |
| Slack timing | Notify-only at end of M22; richer intake polish in M23 if needed |
| Label set | Keep existing four + add `design-system` (six total with `other`) |
| Cursor agent pin | Keep current M21 allowlisted agent id |
| First UI experiment | Design-system / craft tokens demo in sandbox inspired by starred `frontend-ui`/`design-system` repos (not a vendor install) |

## Open questions (optional overrides)

1. Preferred ingress host (GitHub Actions+App vs Render/Fly worker vs other)?
2. Confirm full fixed label list beyond adding `design-system`.
3. Preferred first sandbox UI experiment theme if not the default above?
4. Keep sole M21 agent pin for unattended dispatch, or expand under a new ADR?

## Capability planning appendix (proposals only)

Top Skills: `implementation-planning`, `northstar-connected-routine`,
`github-integration`, `linear-integration`, `technology-intelligence-live`,
`skill-learning-loop`, `candidate-promotion`, `security-review`,
`dependency-supply-chain`, `sandbox-validation`, `react-engineering`,
`playwright-browser-validation`.

No hard capability gaps detected for planning; M22 ingress hosting is the main
greenfield surface.

## Approval record

| Captain | Decision | Date |
|---|---|---|
| Captain | **APPROVED** — M22 implementation in progress (M23 deferred) | 2026-09-09 |
| Captain | **APPROVED** — M23 start after #129 + sandbox#43 merged | 2026-09-10 |

Captain approved plan `m22-m23-northstar-ops-ti-flywheel` on 2026-09-09.
M22 shipped as v1.27.0 (#129). Rollback tag for M23: `rollback/pre-m23-ti-flywheel`.
Branch: `cursor/m23-ti-skill-flywheel-6044`. Implement M23 → v1.28.0.
