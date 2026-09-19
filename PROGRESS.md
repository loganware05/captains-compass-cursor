# Progress

## Current status

**Release: v1.41.0** — M40 Filesystem-Gated Context & Dependency Architecture
shipped 2026-09-19.

| Item | Value |
|---|---|
| Tagged | **v1.41.0** @ `a6039b0` (control #177 merged; sandbox #59 merged) |
| Plan | `m40-filesystem-gated-context` — **COMPLETE** |
| Rollback | `rollback/pre-m40-filesystem-gated-context` @ `125d53e` |
| Evidence | `.agent/evidence/m40-filesystem-gated-context/` |
| Carry-over | Approved by Captain 2026-09-19 for `capability-planning`, `code-reviewer`, `skill-lifecycle` (inodes `captain_approved: true`) |

## In flight

- Nothing. Awaiting next Captain-directed milestone.

## Completed

- **M40 → v1.41.0** — inode store, context route walker, hard/symlink
  dependency graph, boundary review gate (precision 1.0 fixture + sandbox),
  content-addressed Skill inodes, subagent `pwd` isolation; adversarial
  remediation (19 findings) with 26 regression tests
- M39 → v1.40.0 / v1.40.1 (agentic security ingest + opaque forge gate)
- M37 → v1.39.0; Track B complete through B5 / v1.36.0

## Known follow-ups (observed during M40; not in scope)

- M37 specialist `sec-hook-checkout-shortcircuit` fires on *removed* diff lines
  (FP when a diff removes the legacy pattern) — detectors should scan added
  lines only
- `orchestrator/registry/compiler.py` SKILL_SLUGS predates M21/M27: missing
  `code-reviewer` and `northstar-connected-routine` (drift warnings now
  surface both)

## Blockers

None.

## Recommended sequence

1. File follow-up plans for the two known follow-ups above when the Captain
   prioritizes them
