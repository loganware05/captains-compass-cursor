# Progress

## Current status

**Planning: M41 / v1.42.0 (proposed)** — Jev Decision Service shadow-mode
skill suggestion. Plan status **AWAITING APPROVAL**.

| Item | Value |
|---|---|
| On main | **v1.41.0** — M40 filesystem-gated context (#177 / sandbox #59) + closeout (#178) @ `cec4da2` |
| In flight | **M41 plan draft** — branch `cursor/m41-jev-decision-service-753c` |
| Plan | `IMPLEMENTATION_PLAN.md` — **AWAITING APPROVAL** (`m41-jev-decision-service`) |
| Spec | Notion [NorthStar × Jev — Decision Service Implementation Draft](https://app.notion.com/p/3e4e6a901c43819a8173c581b91a04f0) (research only) |
| Prior plan archive | `docs/plans/M40_FILESYSTEM_GATED_CONTEXT.md` |

## In flight

- First Mate drafted M41 implementation plan from the Notion Decision Service
  draft: optional version-pinned Jev provider, **shadow-only** skill suggestion
  vs deterministic matcher, hermetic stub/file default, Captain gates unchanged
- **No product implementation** until Captain approves `IMPLEMENTATION_PLAN.md`

## Completed

- **M40 → v1.41.0** — inode store, context route walker, hard/symlink
  dependency graph, boundary review gate (precision 1.0 fixture + sandbox),
  content-addressed Skill inodes, subagent `pwd` isolation
- M39 → v1.40.0 / v1.40.1 (agentic security ingest + opaque forge gate)
- M37 → v1.39.0; Track B complete through B5 / v1.36.0

## Known follow-ups (deferred; not in M41 unless Captain folds WS0)

1. M37 specialist `sec-hook-checkout-shortcircuit` fires on *removed* diff lines
   (FP when a diff removes the legacy pattern) — detectors should scan added
   lines only
2. `orchestrator/registry/compiler.py` SKILL_SLUGS predates M21/M27: missing
   `code-reviewer` and `northstar-connected-routine` (compile drift warnings;
   optional M41 WS0)

## Blockers

Awaiting Captain approval of `m41-jev-decision-service` (or revision /
rejection / reprioritization vs the two follow-ups above).

## Recommended sequence

1. Captain review + approve/revise `IMPLEMENTATION_PLAN.md` (M41)
2. On approval: issue, rollback tag, implement shadow DecisionProvider
3. Separately prioritize M37 removed-line FP and/or SKILL_SLUGS micro-fix
