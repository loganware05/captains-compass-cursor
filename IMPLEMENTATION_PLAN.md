# Implementation Plan — Audit P3 OpenUI Local Viewer

- Status: **APPROVED** (implementation in progress)

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `audit-p3-openui-viewer` |
| Issue | [#291](https://github.com/loganware05/captains-compass-cursor/issues/291) |
| PR | [#292](https://github.com/loganware05/captains-compass-cursor/pull/292) |
| Baseline | `origin/main` @ `257a8e7` / **v1.88.0** tip after #290 |
| Branch | `feature/291-audit-p3-openui-viewer` |
| Rollback | `rollback/pre-audit-p3-openui-viewer` @ `257a8e7` |
| Proposed release | **v1.89.0** |
| Created | 2026-11-22 |
| Approved by | Logan Ware (Captain) — 2026-11-22 |

Budget: `.agent/budgets/audit-p3-openui-viewer.md`  
Durable copy: `docs/plans/AUDIT_P3_OPENUI_VIEWER.md`  
Evidence: `.agent/evidence/audit-p3-openui-viewer/`

## Approval decisions

| Q | Decision |
|---|---|
| Q1 Viewer-only (not full P3 trio) | **yes** |
| Q2 File preview + optional localhost | **yes** |
| Q3 Prefer T3/Bend instead | **no** |
| Q4 Release train | **v1.89.0** |

## Scope delivered

### W1 — Preview / serve

- `orchestrator/openui/preview.py` — HTML viewer from persisted `*.openui`
- `northstar ui preview|serve` via `scripts/run-openui.sh`
- Static mock → `preview.sample.html`; package `preview.html` redirects to sample
- Hermetic tests in `tests/orchestrator/test_openui_preview.py`

### W2 — Docs / doctor

- Doctor asserts preview module + writes preview HTML
- CHANGELOG / TESTING / handbook-adjacent docs / ADR-112

## Out of scope (deferred)

T3 live · specialized real eval · B4 FIX→SUBMIT · XRV ops-verified · branch prune · Bend #278

## Acceptance criteria

- [x] Preview real emitted surface without hand-editing HTML
- [x] Hermetic emit → preview test
- [x] Approve/reject gates unchanged
- [x] doctor + `tests/run.sh` green; evidence recorded
- [x] PR from `main`; rollback tag cited ([#292](https://github.com/loganware05/captains-compass-cursor/pull/292))
