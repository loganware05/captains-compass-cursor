# Implementation Plan — M38 / Phase C Shell forge gate

> Archive mirror of root `IMPLEMENTATION_PLAN.md` (plan id `m38-shell-forge-gate`).


## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `m38-shell-forge-gate` |
| Supersedes | Completes ADR-053 residual + M37 Phase C |
| Product | **NorthStar** |
| Baseline | **v1.39.0** (M37 on main via this closeout PR) |
| Prepared | 2026-09-18 |
| Design source | ADR-053 residual; Cursor Agentic Security Review class (shell bypass of plan gate) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.39.1** (or v1.40.0 if bundled with Phase B) |
| Rollback tag | `rollback/pre-m38-shell-forge-gate` |
| Branch | `cursor/m38-shell-forge-gate-3b10` (after approval) |
| Issue | [#169](https://github.com/loganware05/captains-compass-cursor/issues/169) |
| Captain | Logan Ware |

## Problem

M36 closed Write/StrReplace self-serve of plan approval. Agents can still forge
`IMPLEMENTATION_PLAN.md` via shell (`echo`/`tee`/`cat >`/`printf`) and commit,
unlocking product edits. ADR-053 tracked this as residual Phase C.

## Scope

1. Add fail-closed `beforeShellExecution` check (extend `plan-approval-check.sh`
   or sibling hook registered in `hooks.json`) that denies commands which write
   to `IMPLEMENTATION_PLAN.md` when the payload/command promotes Status to
   APPROVED/IN PROGRESS/VALIDATING/COMPLETE **unless** `COMPASS_CAPTAIN_APPROVE=1`.
2. Cover common forge patterns: `>`, `>>`, `tee`, `cat`/`printf`/`echo` redirects.
3. Hermetic tests for deny/allow cases; doctor unchanged locks.
4. Evidence under `.agent/evidence/m38-shell-forge-gate/`.

## Non-goals

- Live Cursor Security Agent ingestion (Phase B / M39 — separate plan)
- Track C3 connected routine
- Weakening plan-approval Write gate from M36

## Acceptance criteria

1. Plan-gated (this doc)
2. Shell forge promoting APPROVED without Captain env → deny
3. Captain env / non-promoting plan edits → allow
4. Hermetic tests + doctor green
5. Docs/ADR update; product hook refresh note if install path affected

## Approval gate

**AWAITING APPROVAL** — Captain: “I approve IMPLEMENTATION_PLAN.md for m38-shell-forge-gate”.
