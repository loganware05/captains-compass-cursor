# Progress

## Current status

**IN PROGRESS:** [#278](https://github.com/loganware05/captains-compass-cursor/issues/278)
`bend-policy-proof-spike` (plan **APPROVED** 2026-11-18) on `feature/278-bend-policy-proof-spike`
— opt-in Bend 2 proof experiment for the policy lifecycle decision core. Baseline **v1.87.0** @ `ef0ca32`;
rollback `rollback/pre-bend-policy-proof-spike`. **Waves 0, A, B, C implemented; awaiting Captain review/PR.**

| Item | Value |
|---|---|
| Proofs | 17 laws (incl. P11 liveness), `bend PROOF.bend --verdict` → ALL PROOFS CHECK (Bend 2.0.40, Lean 4.34.0) |
| Conformance | 1568-row exhaustive grid, 0 diffs vs real `can_transition`/`require_captain_approved` |
| Mutation controls | 38/38 rejected: 23 model mutants (19 by proofs, 18 by the evidence grid) + 15 Python-side (9 grid-visible; 6 evasions caught only by the AST-pin lock) |
| Validation | `tests/run.sh` 137/0 with and without the gate; formal unit tests 56 OK; doctor 0 errors |
| Finding | 001 direct entry into `proven` bypasses all gates (reported, not fixed; outside the model) |
| ADR | ADR-110 **Proposed** — Captain decides go/no-go |

**Captain attention:**

1. **Scope narrowing (Amendment A1):** P4/P5 are proved *per accepted step*, not over whole histories as
   the approved plan said. Declared in the plan, ADR and docs.
2. **Laws review:** `LAWS.bend` / `SPEC.bend` are Captain-owned; `--strict-laws --base-ref origin/main`
   fails on this branch by design until you review them.
3. **Pre-existing flake (not fixed, out of scope):** `doctor.sh` can fail
   `northstar help missing Surfaces map (C1)` (`grep -q` + `pipefail` SIGPIPE; 4/300 on `origin/main`).
4. Known limits (see ADR-110): P6/P8/P10 are model-internal, not linked to production code; the `promote_policy` pin is a coarse whole-function AST hash (any edit there needs a re-lock); Lean is not pinned; `--base-ref` is caller-chosen.
5. Merge is Captain-only.

### Previous

**MERGED:** [#275](https://github.com/loganware05/captains-compass-cursor/pull/275)
for [#274](https://github.com/loganware05/captains-compass-cursor/issues/274)
`post-merge-wave-continue` → **v1.87.0** @ `6ee5fb6`.

| Item | Value |
|---|---|
| Baseline | **v1.86.0** @ `9e2c0d1` |
| Plan | `post-merge-wave-continue` **COMPLETE** |
| Issue | [#274](https://github.com/loganware05/captains-compass-cursor/issues/274) |
| PR | [#275](https://github.com/loganware05/captains-compass-cursor/pull/275) |
| Tag | `v1.87.0` (on merge commit) |
| Rollback | `rollback/pre-post-merge-wave-continue` @ `9e2c0d1` |

### Prior closeout

- Superpowers + C2 session memory **v1.86.0** (#273)
- XRV W3 **v1.85.0** (#267) + docs (#269)
- PrizePicksBot Pilot C [#3](https://github.com/loganware05/PrizePicksBot/pull/3); EER #270
- TrapHouse Pilot A [#37](https://github.com/loganware05/TrapHouseKitchen/pull/37)
- Bitcoin Pilot B [#18](https://github.com/loganware05/bitcoin-data-collector/pull/18)

### External witness (2026-11-16)

- **RedTailEnergy / OpenRemote** (AABE hackathon) witnessed via XRV product readiness + portfolio assess
  - Product: https://github.com/loganware05/RedTailEnergy/commit/92323390a2549ef80bb912b7eb6c5d538b7d0200
  - Evidence: `.agent/evidence/xrv/redtail-openremote-2026-11-16/`
  - EER: `.agent/evidence/xrv/eer-redtail-openremote-telemetry.json` (`lifecycle_state=merged`, observe-only)
  - Outcome: Demo Controls Headcount↔Occupancy + battery/solar/load married to cloudy-night OR hour; Packs Ready retained

## Standing order

Approve ⇒ implement → validate → commit → open PR. Merge remains Captain-only.

## Blockers

None.
