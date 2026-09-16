# Implementation Plan — M34 / C1 Single launcher UX

> Archive mirror of root `IMPLEMENTATION_PLAN.md` (plan id `c1-single-launcher-ux`).


## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING_APPROVAL** |
| Plan ID | `c1-single-launcher-ux` |
| Supersedes | `b5-precision-ledger` (CLOSED — shipped as v1.36.0 / M33 / B5) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.36.0` / `origin/main` (M33 merged, PR #160) |
| Prepared | 2026-09-16 |
| Approved | — |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track C / **C1** |
| Linear | [OVA-50](https://linear.app/ovaltechnologysolutions/issue/OVA-50) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.37.0** |
| Rollback tag | `rollback/pre-c1-single-launcher-ux` (create after approval) |
| Branch | (create after approval) `cursor/m34-c1-single-launcher-ux-3b10` |
| Issue | [#161](https://github.com/loganware05/captains-compass-cursor/issues/161) |
| Captain | Logan Ware |
| Queue | `.agent/queues/captain-objectives-2026-09-15.md` |

## Captain locks (binding)

1. **Captain plan gate** — no product implementation until this plan is explicitly approved
2. **No control-script copy into product repos** — full product install is **C2**, not C1
3. **Linear records only** — never treat Linear as approval origin
4. **Hermetic CI** — default tests/doctor remain network-free
5. **`approved_for_execution` stays false** for Stars TI candidates
6. **Skill slug** — `code-reviewer` unchanged
7. **Never auto-merge** — repair / review GitHub surfaces stay human-reviewed
8. **No silent reputation mutation** — B5 precision proposal-only locks unchanged
9. **Topology-free launcher remains canonical** — `scripts/northstar` stays the agent-facing entrypoint
10. **Docs over rewrites** — prefer help/docs/index clarity before inventing new CLIs

## Request (Captain-level)

Approve planning for **M34 / C1 — Single launcher UX**: make `northstar skills …`, `northstar review …`, and related surfaces (`outcomes`, `repair`, `precision`, `intent`) feel like one product via unified help, a docs index, and a clear product-repo install path (pointers / onboarding — not full C2 install).

## Problem statement

1. Track B (M27–M33) shipped review → outcomes → repair → precision, but launcher help and docs still read as bolted-on families.
2. Roadmap C1 exit: *Help text, docs index, install path into product repos*.
3. Operators bouncing between Learning Loop and Code Reviewer need one mental model without waiting for C2 bitcoin-data-collector install.

## Non-goals

- Full product-repo install of NorthStar into `bitcoin-data-collector` (that's **C2**)
- Copying control `scripts/` into product repos
- New webhook / PR-event automation (C3)
- Eval harness / golden diffs (C4)
- Changing Skill slug `code-reviewer`
- Auto-apply of precision / routing proposals
- Expanding B4 live FIX beyond packet MVP

## Dependencies

| Dep | Status |
|---|---|
| Track B Code Reviewer (B0–B5 / M27–M33) | **Done** (v1.30.0–v1.36.0) |
| `scripts/northstar` topology launcher (M24) | **Done** |
| `scripts/install.sh` + product onboarding docs | **Exists** (needs UX polish / index, not rewrite) |

## Acceptance criteria

1. **Plan-gated** — implementation starts only after Captain approves this document.
2. **Unified help** — `northstar help` (and `--help`) lists skills / review / intent / outcomes / repair / precision with one-line purpose each and points to docs index.
3. **Docs index** — a single docs entry (new or extended) linking Learning Loop guides + Code Reviewer integration + precision/repair/outcomes in operator order.
4. **Install path clarity** — `install.sh` help + onboarding docs state what lands in a product repo vs what stays control-only; no control-script copy.
5. **Doctor + smoke** — hermetic check that help text mentions the shipped surfaces; optional unittest/golden help snippet.
6. **Docs** — ADR-051 (or next free), CHANGELOG / VERSION → **1.37.0**, PROGRESS / DECISIONS updated.
7. **No product implementation beyond UX/docs** — C2 remains a separate plan.

## Architecture (proposed)

```
scripts/northstar  ──► unified help / surface map
        │
        ├─ docs/INDEX (or equivalent) ──► skills + review + precision/repair
        └─ install.sh / PRODUCT_ONBOARDING ──► product path (docs/Skills only)
```

## Implementation steps (after approval only)

1. Create rollback tag `rollback/pre-c1-single-launcher-ux`.
2. Expand `northstar` help + related usage text.
3. Add/extend docs index; cross-link integrations + guides.
4. Clarify install/onboarding product vs control boundary.
5. Doctor / smoke + VERSION 1.37.0 + ADR.
6. Open PR to `main`; Captain merge → tag **v1.37.0**.

## Validation plan

| Layer | How |
|---|---|
| Static | doctor.sh |
| Unit/smoke | help text contains required surface names |
| Docs | index links resolve in-repo |
| Security | no new secrets; install still skip-if-exists |
| Rollback | revert PR / reset to rollback tag |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Scope creep into C2 product install | Explicit non-goal; separate plan |
| Help sprawl | One-line purposes + docs index, not duplicate manuals |
| Breaking agent scripts | Keep existing subcommands; additive help only |

## Budget

After approval: `.agent/budgets/c1-single-launcher-ux.md`

Soft stop: AC + tests/smoke + evidence + PR. Hard stop: no control-script copy; no C2 install; no model-in-CI default.

## Rollback

1. Revert the C1 PR or reset to rollback tag.
2. Confirm `northstar` skills/review/precision still work.
3. VERSION/CHANGELOG note if tag already cut.

## Open questions (for Captain, non-blocking)

1. Prefer new `docs/INDEX.md` vs extending `docs/PRODUCT_ONBOARDING.md`?
2. After C1, jump to **C2** product install on `bitcoin-data-collector`, or finish Learning Run / OVA-45 retain first?

## Approval gate

**AWAITING_APPROVAL** — reply with:

`I approve IMPLEMENTATION_PLAN.md for c1-single-launcher-ux`

No product implementation until that utterance (or equivalent explicit approval) is recorded.
