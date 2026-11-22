# Bend ADR-110 Go + Entry-State Law (durable plan copy)

> Plan ID `bend-adr-110-go` — **COMPLETE**. Issue [#278](https://github.com/loganware05/captains-compass-cursor/issues/278).
> Budget: `.agent/budgets/bend-adr-110-go.md`. Evidence: `.agent/evidence/bend-adr-110-go/`.

## Goal

Accept ADR-110 as conditional-go and add Finding 001 entry-state Bend law
(birth-in-`candidate`). Keep opt-in; no CI wire; no target widen.

## Baseline

`origin/main` @ `843af00` / **v1.90.0**. Release **v1.91.0**.
Rollback: `rollback/pre-bend-adr-110-go` @ `843af00`.

## Delivered

- ADR-110 Accepted
- P12 `p12_entry_candidate`
- Formal check evidence (proofs pass, 38/38 mutants, entry probe closed)
