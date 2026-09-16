# Implementation Plan — M35 / C2 Product-repo install (bitcoin-data-collector)

> Archive mirror of root `IMPLEMENTATION_PLAN.md` (plan id `c2-product-repo-install`).


## Metadata

| Field | Value |
|---|---|
| Status | **SHIPPED** (control evidence / v1.38.0; product PR pending Captain push) |
| Plan ID | `c2-product-repo-install` |
| Supersedes | `c1-single-launcher-ux` (CLOSED — shipped as v1.37.0 / M34 / C1) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.37.0` / `origin/main` (M34 merged, PR #163) |
| Prepared | 2026-09-16 |
| Approved | 2026-09-16 — Captain: “I approve IMPLEMENTATION_PLAN.md for c2-product-repo-install” |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track C / **C2** |
| Linear | [OVA-51](https://linear.app/ovaltechnologysolutions/issue/OVA-51) |
| Control repo | `loganware05/captains-compass-cursor` |
| Target product | `loganware05/bitcoin-data-collector` |
| Proposed release | **v1.38.0** (control) + product install PR |
| Rollback tag | `rollback/pre-c2-product-repo-install` |
| Branch | `cursor/m35-c2-product-repo-install-3b10` |
| Issue | [#164](https://github.com/loganware05/captains-compass-cursor/issues/164) |
| Captain | Logan Ware |

## Acceptance criteria

1. **Plan-gated** ✅
2. **Product install** — local install succeeded; product PR push blocked (403) — patch in evidence for Captain ✅ (partial)
3. **No scripts/** ✅ (inventory)
4. **Memory preserved** ✅ (new templates; Cloud Agent files preserved)
5. **Operator path documented** ✅ (`docs/INDEX.md` product-scoped + APPLY.md)
6. **Control evidence** ✅ `.agent/evidence/c2-product-repo-install/`
7. **Control docs** — ADR-052; VERSION **1.38.0** ✅
8. **Doctor/tests** — control hermetic checks remain green ✅

## Residual

Captain must apply `.agent/evidence/c2-product-repo-install/APPLY.md` (or grant
write access) to open/merge the bitcoin-data-collector PR for full C2 exit.

## Approval gate

**APPROVED** 2026-09-16 — Captain: “I approve IMPLEMENTATION_PLAN.md for c2-product-repo-install”.
