# Implementation Plan — M35 / C2 Product-repo install (bitcoin-data-collector)

> Archive mirror of root `IMPLEMENTATION_PLAN.md` (plan id `c2-product-repo-install`).


## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING_APPROVAL** |
| Plan ID | `c2-product-repo-install` |
| Supersedes | `c1-single-launcher-ux` (CLOSED — shipped as v1.37.0 / M34 / C1) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.37.0` / `origin/main` (M34 merged, PR #163) |
| Prepared | 2026-09-16 |
| Approved | — |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track C / **C2** |
| Linear | [OVA-51](https://linear.app/ovaltechnologysolutions/issue/OVA-51) |
| Control repo | `loganware05/captains-compass-cursor` |
| Target product | `loganware05/bitcoin-data-collector` |
| Proposed release | **v1.38.0** (control evidence/docs) + product install PR |
| Rollback tag | `rollback/pre-c2-product-repo-install` (create after approval) |
| Branch | (create after approval) `cursor/m35-c2-product-repo-install-3b10` |
| Issue | [#164](https://github.com/loganware05/captains-compass-cursor/issues/164) |
| Captain | Logan Ware |
| Queue | `.agent/queues/captain-objectives-2026-09-15.md` |

## Captain locks (binding)

1. **Captain plan gate** — no product implementation until this plan is explicitly approved
2. **No control-script copy** — product never receives control `scripts/` (including `northstar`)
3. **Memory docs preserved** — skip-if-exists; never clobber `PROJECT_CONTEXT.md` / plans / DECISIONS
4. **Sandbox-first if uncertain** — prefer proving install dry-run on `captain-compass-sandbox` before bitcoin-data-collector if Captain requests
5. **Linear records only** — never treat Linear as approval origin
6. **Hermetic CI** on control — default tests/doctor remain network-free
7. **`approved_for_execution` stays false** for Stars TI candidates
8. **Skill slug** — `code-reviewer` unchanged
9. **Never auto-merge** — product install PR stays human-reviewed
10. **Run from control** — operators use control `northstar … --repo <product>`

## Request (Captain-level)

Approve planning for **M35 / C2 — Product-repo install**: install NorthStar docs/Skills into `bitcoin-data-collector` without control scripts, preserve memory docs, and record evidence + operator path.

## Problem statement

1. C1 unified the launcher and install boundary docs, but bitcoin-data-collector still lacks a maintained NorthStar product install.
2. Roadmap C2 exit: *`install.sh` into product; memory docs preserved*.
3. Without an explicit plan, install risk is clobbering product memory or sneaking control scripts into the product tree.

## Non-goals

- Copying control `scripts/` into the product repo
- Changing bitcoin-data-collector application behavior beyond workflow install
- C3 connected routine / webhooks / PR events
- C4 eval harness
- Auto-apply of precision / routing proposals
- Expanding B4 live FIX beyond packet MVP

## Dependencies

| Dep | Status |
|---|---|
| C1 — Single launcher UX (M34) | **Done** (v1.37.0) |
| `scripts/install.sh` + product INDEX template | **Done** |
| Track B Code Reviewer | **Done** |
| Access to `loganware05/bitcoin-data-collector` | Assumed (Captain-owned) |

## Acceptance criteria

1. **Plan-gated** — implementation starts only after Captain approves this document.
2. **Product install PR** — dedicated branch/PR on bitcoin-data-collector from `install.sh` (or documented dry-run + PR).
3. **No scripts/** — evidence proves product tree has no control `scripts/northstar` (or `scripts/` control package).
4. **Memory preserved** — existing product memory docs not overwritten; `.agent/COMPASS_VERSION` records control version.
5. **Operator path documented** — product INDEX / onboarding note: run `northstar` from control with `--repo`.
6. **Control evidence** — `.agent/evidence/c2-product-repo-install/` with install log, file inventory, doctor (if applicable).
7. **Control docs** — ADR-052 (or next free), PROGRESS / CHANGELOG / VERSION → **1.38.0** for control closeout of the install path (even if product PR is separate).
8. **Doctor/tests** — hermetic control checks remain green; no weakening.

## Architecture (proposed)

```
control: scripts/install.sh
        │
        ▼
bitcoin-data-collector (branch)
  ├─ .cursor/ Skills/rules/agents
  ├─ docs/INDEX.md (product-scoped template)
  ├─ memory docs (skip-if-exists)
  └─ .agent/COMPASS_VERSION
        │
        └─ operators: CONTROL/scripts/northstar … --repo <product>
```

## Implementation steps (after approval only)

1. Create rollback tag `rollback/pre-c2-product-repo-install` on control.
2. Clone/checkout bitcoin-data-collector; create install branch.
3. Run control `install.sh` into product; review diff; open product PR.
4. Capture inventory evidence (no scripts copy; memory preserved).
5. Update control docs/ADR/VERSION 1.38.0 + evidence.
6. Open control PR; Captain merges both as needed → tag **v1.38.0**.

## Validation plan

| Layer | How |
|---|---|
| Static | control doctor.sh |
| Install proof | product tree inventory + COMPASS_VERSION |
| Security | no secrets committed; no control scripts in product |
| Rollback | revert product PR; control reset to rollback tag |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Clobber product memory | skip-if-exists already in install.sh; review PR carefully |
| Accidental scripts copy | inventory assertion in evidence + tests |
| Scope into app code changes | Explicit non-goal |
| Repo access / branch protection | Captain merge on product PR |

## Budget

After approval: `.agent/budgets/c2-product-repo-install.md`

Soft stop: AC + evidence + PRs. Hard stop: no control-script copy; no memory clobber; no Linear approval origin.

## Rollback

1. Revert product install PR and/or control docs PR.
2. Reset control to rollback tag if needed.
3. VERSION/CHANGELOG note if tag already cut.

## Open questions (for Captain, non-blocking)

1. Install directly on **bitcoin-data-collector**, or prove once more on **captain-compass-sandbox** first?
2. After C2, prefer **C3 connected routine** or finish Learning Run / OVA-45 retain?

## Approval gate

**AWAITING_APPROVAL** — reply with:

`I approve IMPLEMENTATION_PLAN.md for c2-product-repo-install`

No product implementation until that utterance (or equivalent explicit approval) is recorded.
