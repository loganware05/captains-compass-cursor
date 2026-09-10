# Implementation Plan — M22/M23 NorthStar live ops + TI skill flywheel

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED — M22 SHIPPED; M23 IN PROGRESS** |
| Plan ID | `m22-m23-northstar-ops-ti-flywheel` |
| Supersedes | `issue-50-northstar-m4-bridge` (CLOSED — shipped as v1.26.0) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.27.0` on `main` (M22 shipped) |
| Prepared | 2026-09-09 |
| Start gate | Open — Captain approved 2026-09-09; directed M23 start 2026-09-10 |
| M22 | [#129](https://github.com/loganware05/captains-compass-cursor/pull/129) merged; sandbox [#43](https://github.com/loganware05/captain-compass-sandbox/pull/43) merged |
| M23 branch | `cursor/m23-ti-skill-flywheel-6044` |
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

1. NorthStar connected routine was fixture-proven; M22 added unattended live ingress.
2. Stars TI can categorize starred repos, but lacked a first-class
   **security + supply-chain + usefulness-label** scorecard before Skill drafts.
3. Skill learning loop can propose improvements, but did not enforce deeper gates,
   and did not drive bounded sandbox UI experiments as evidence for design-oriented Skills.

## Milestone status

### M22 — NorthStar Unattended Connected Ops → **v1.27.0** — SHIPPED

Unattended GitHub + Linear (then Slack notify/intake) feed the NorthStar routine
without weakening fail-closed approval. Sandbox is the only product
dispatch/allowlist target.

Shipped via [#129](https://github.com/loganware05/captains-compass-cursor/pull/129)
and sandbox [#43](https://github.com/loganware05/captain-compass-sandbox/pull/43).

### M23 — TI Scorecard + Skill Flywheel → **v1.28.0** — IN PROGRESS

Starred-only TI → fixed usefulness labels → mandatory security + supply-chain
evidence → Skill drafts → bounded sandbox UI experiments → Captain-gated
Skill/procedure promotion.

## Acceptance criteria

### M22 (v1.27.0) — met

- [x] Unattended ingress with signature verification + idempotent delivery handling
- [x] Live GitHub approval via plan digest only; Slack/Linear cannot approve
- [x] Live Linear ledger; Slack notify after GH+Linear
- [x] Fixture mode CI default; live mode Captain-gated
- [x] Sandbox-only product allowlist; no auto-merge/release/Skill install
- [x] Docs, doctor, tests, sandbox refresh, release **v1.27.0**

### M23 (v1.28.0)

- [ ] Fixed usefulness/category label set extended at least with **`design-system`**
- [ ] TI paths enforce **starred provenance** for external repo entry
- [ ] Before any Skill draft: required **security-review** +
      **dependency-supply-chain** evidence artifacts; fail closed if missing
- [ ] `skill-learning-loop` / apply-improvement enforce the new gates; live apply
      remains `--captain-approved` only
- [ ] At least one **bounded UI experiment** in `captain-compass-sandbox` with
      Playwright/a11y evidence linked from control validation docs
- [ ] Example path supported for a **starred** design repo (categorize → scorecard
      → draft proposal; no auto Skill install)
- [ ] `approved_for_execution` stays false for TI candidates; no clone/exec of
      starred repos from learning/TI
- [ ] Sandbox refresh + smoke gate for **1.28.0**
- [ ] Tag/release **v1.28.0** + rollback tag `rollback/pre-m23-ti-flywheel`

## Non-goals

- Moving approval authority to Slack, Linear, or Notion
- Auto-merge / auto-release / unattended live Skill install
- Installing Compass into non-sandbox product repos in these milestones
- Arbitrary non-starred URL ingest into TI
- Cloning or executing third-party repos inside the control learning loop
- Reopening closed #50 / v1.26.0 / v1.27.0 scope
- Multi-tenant hosted SaaS control plane

## Safety and authority

- GitHub + plan digest remain the sole engineering approval authority (ADR-037/039).
- Slack / Linear / Notion are never approval or dispatch authorities.
- No auto-merge, auto-release, or unattended live Skill install.
- Secrets never enter prompts, logs, Slack, Linear, GitHub mirrors, or fixtures.
- TI candidates remain non-executable (`approved_for_execution: false`).
- Wrong Cursor agent → fail closed.
- Sandbox-only product target for M22/M23.
- Routing weight apply and live Skill apply remain explicit Captain gates.

## Approval record

| Captain | Decision | Date |
|---|---|---|
| Captain | **APPROVED** plan; M22 via #129 | 2026-09-09 |
| Captain | **Directed M23 start** after #129 + sandbox#43 merged | 2026-09-10 |

Captain approved plan `m22-m23-northstar-ops-ti-flywheel` on 2026-09-09.
M22 shipped as **v1.27.0**. M23 proceeds toward **v1.28.0**.
