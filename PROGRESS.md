# Progress

## Current status

**In flight: M40 / v1.41.0** — Filesystem-Gated Context & Dependency
Architecture (Captain-approved 2026-09-18).

| Item | Value |
|---|---|
| On main | **v1.40.1** — M39 (#175) + M38 residual (#174) + closeout (#176) |
| In flight | **M40** — control PR [#177](https://github.com/loganware05/captains-compass-cursor/pull/177); sandbox PR [#59](https://github.com/loganware05/captain-compass-sandbox/pull/59) |
| Branch | `cursor/m40-filesystem-gated-context-ea39` (both repos) |
| Plan | `IMPLEMENTATION_PLAN.md` — **APPROVED — IMPLEMENTING** (`m40-filesystem-gated-context`) |
| Rollback | `rollback/pre-m40-filesystem-gated-context` @ `125d53e` |
| Evidence | `.agent/evidence/m40-filesystem-gated-context/` |

## In flight

- M40 WS1–WS7 implemented; validation green (doctor 0/0, suite 125, orchestrator
  432, evals 44); sandbox boundary precision **1.0** (3/3 seeded detected, 0 FP
  on clean change); payload reduction 52% on fixture corpus
- Remaining: Captain review of PR #177 / sandbox #59, merge, tag **v1.41.0**
- Carry-over pending Captain: `capability-planning`, `code-reviewer`,
  `skill-lifecycle` skill inodes (edited in M40) — approve via
  `./scripts/build-skill-inodes.sh --captain-approved`

## Completed

- M39 → v1.40.0 / v1.40.1 (agentic security ingest + opaque forge gate)
- M37 → v1.39.0; Track B complete through B5 / v1.36.0

## Known follow-ups (observed during M40; not in scope)

- M37 specialist `sec-hook-checkout-shortcircuit` fires on *removed* diff lines
  (FP when a diff removes the legacy pattern) — detectors should scan added
  lines only
- `orchestrator/registry/compiler.py` SKILL_SLUGS predates M21/M27: missing
  `code-reviewer` and `northstar-connected-routine` (pre-existing on main)

## Blockers

None.

## Recommended sequence

1. Captain review + merge control PR #177 and sandbox PR #59
2. Tag **v1.41.0**; approve skill-inode carry-over for the three edited Skills
3. File follow-up plans for the two known follow-ups above
