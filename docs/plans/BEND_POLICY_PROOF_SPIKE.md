# Bend Policy-Lifecycle Proof Spike (durable plan copy)

> **APPROVED** (Captain, 2026-11-18) — issue [#278](https://github.com/loganware05/captains-compass-cursor/issues/278),
> plan ID `bend-policy-proof-spike`. Decisions: Q1 replace active plan; Q2 lifecycle only; Q3 isolated local
> toolchain; Q4 default budget; Q5 `LAWS.bend` Captain-reviewed. Active gate text lives in the
> root `IMPLEMENTATION_PLAN.md` while it is the active plan; this file is the durable copy.
> Budget: `.agent/budgets/bend-policy-proof-spike.md`. Source: Captain thread
> 62fcd31d-9f2e-448b-943b-14022585e272 (Bend assessment, 2026-11-18).

## Goal

Learn, with a small opt-in experiment, whether Bend 2 formal proofs give NorthStar stronger
evidence for a safety-critical decision core, before any wider adoption. Bend pin:
`bendlang/bend@9c586f094f4fc88bef440dc8b4d77a2f92c257cc` (Apache-2.0; re-confirm at start).

## Target

`orchestrator/behavior/policy/states.py` (7 states, `TRANSITIONS`, `CAPTAIN_REQUIRED`,
`can_transition`) plus the decision order in `promote.py` / `gates.py`. Evidence gates that read
the filesystem are modeled as boolean preconditions only.

## Proposed properties (P1–P6)

1. P1 legality: accept ⇒ edge in transition table.
2. P2 Captain gate: accept ∧ target ∈ `CAPTAIN_REQUIRED` ⇒ `captain_approved`.
3. P3 `retired` is terminal.
4. P4 acyclic/monotone over arbitrary accepted sequences.
5. P5 `shadowed` precedes `approved` in any accepted history.
6. P6 the model has no output granting execution authority.

## Waves

- **Wave 0** — supply-chain review, pinned isolated build (no unreviewed `curl | sh`), trivial
  proof + `--verdict`. Stop gate if not reproducible within budget.
- **Wave A** — `formal/bend/policy-lifecycle/` model, Captain-owned `LAWS.bend`, proofs P1–P6.
- **Wave B** — Python↔model exhaustive differential test, drift test, mutation suite, evidence
  record, opt-in `COMPASS_BEND_PROOF_ENABLED=1 ./scripts/northstar formal check policy-lifecycle`
  (skips when Bend absent).
- **Wave C** — report, ADR (go / no-go), docs updates.

## Non-goals

No production rewrite, no performance/GPU work, no hooks/JSON/filesystem modeling, no planner
proofs, no change to promotion semantics or authority locks, no required dependency.

## Decision gate

Go only if all properties are proved, 100% of injected mutations are rejected, conformance is
exhaustive and passing, and there is ≥1 real finding or demonstrably lower review cost than
tests alone. Otherwise archive as docs/evidence.

## Key risks

Proof ≠ production code (mitigated by conformance + drift tests); agent weakening laws
(Captain-owned `LAWS.bend`, compared against `main`); unaudited compiler / unproven parser
(`--verdict`, mutation controls, never sole gate); supply chain; macOS toolchain friction.

## Open questions

Q1 active plan file vs. park under `docs/plans/`; Q2 lifecycle only vs. add planner graph; Q3 local
toolchain build vs. container; Q4 budget; Q5 `LAWS.bend` ownership.

See the root `IMPLEMENTATION_PLAN.md` for the full acceptance criteria, validation plan, and
rollback instructions.
