# Implementation Plan — M34 / C1 Single launcher UX

## Metadata

| Field | Value |
|---|---|
| Status | **SHIPPED** (via this PR / v1.37.0) |
| Plan ID | `c1-single-launcher-ux` |
| Supersedes | `b5-precision-ledger` (CLOSED — shipped as v1.36.0 / M33 / B5) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.36.0` / `origin/main` (M33 merged, PR #160) |
| Prepared | 2026-09-16 |
| Approved | 2026-09-16 — Captain: “I approve IMPLEMENTATION_PLAN.md for c1-single-launcher-ux” |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track C / **C1** |
| Linear | [OVA-50](https://linear.app/ovaltechnologysolutions/issue/OVA-50) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.37.0** |
| Rollback tag | `rollback/pre-c1-single-launcher-ux` |
| Branch | `cursor/m34-c1-single-launcher-ux-3b10` |
| Issue | [#161](https://github.com/loganware05/captains-compass-cursor/issues/161) |
| Captain | Logan Ware |
| Queue | `.agent/queues/captain-objectives-2026-09-15.md` |

## Captain locks (binding)

1. **Captain plan gate** — no product implementation until this plan is explicitly approved ✅
2. **No control-script copy into product repos** — full product install is **C2**, not C1 ✅
3. **Linear records only** — never treat Linear as approval origin
4. **Hermetic CI** — default tests/doctor remain network-free ✅
5. **`approved_for_execution` stays false** for Stars TI candidates
6. **Skill slug** — `code-reviewer` unchanged
7. **Never auto-merge** — repair / review GitHub surfaces stay human-reviewed
8. **No silent reputation mutation** — B5 precision proposal-only locks unchanged
9. **Topology-free launcher remains canonical** — `scripts/northstar` stays the agent-facing entrypoint ✅
10. **Docs over rewrites** — prefer help/docs/index clarity before inventing new CLIs ✅

## Acceptance criteria

1. **Plan-gated** ✅
2. **Unified help** — surface map for skills/review/intent/outcomes/repair/precision ✅
3. **Docs index** — `docs/INDEX.md` ✅
4. **Install path clarity** — install.sh + PRODUCT_ONBOARDING boundary ✅
5. **Doctor + smoke** ✅
6. **Docs** — ADR-051; VERSION **1.37.0** ✅
7. **No C2 product implementation** ✅

## Validation

| Layer | Result |
|---|---|
| Static | doctor.sh passed (help surfaces + INDEX; product-scoped `templates/docs/INDEX.md`) |
| Unit/smoke | `test_m34_c1_single_launcher_ux.py` + `InstallBoundaryTests` (hermetic product INDEX links) |
| Docs | Control `docs/INDEX.md` + product `templates/docs/INDEX.md` (install copies product-scoped) |
| Rollback | `rollback/pre-c1-single-launcher-ux` |

## Open questions (resolved)

1. Prefer new `docs/INDEX.md` — **yes**.
2. After C1: Captain chooses Learning Run retain vs C2.

## Approval gate

**APPROVED** 2026-09-16 — Captain: “I approve IMPLEMENTATION_PLAN.md for c1-single-launcher-ux”.

Shipped on `cursor/m34-c1-single-launcher-ux-3b10`.
