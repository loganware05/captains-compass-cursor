# Progress

## Current status

**Release candidate: v1.35.0** — M32 / B4 Repair loop implementing on
`cursor/m32-b4-repair-loop-3b10`
([issue #154](https://github.com/loganware05/captains-compass-cursor/issues/154)).

| Item | Value |
|---|---|
| Release target | **v1.35.0** (RC — not tagged until Captain merges) |
| M32 / B4 | Repair loop FIND→PROVE→FIX→TEST→SUBMIT (implementing) |
| Issue | [#154](https://github.com/loganware05/captains-compass-cursor/issues/154) |
| Rollback | `rollback/pre-b4-repair-loop` |
| Prior baseline | v1.34.0 / M31 ([release](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.34.0)) |

## Captain objective queue (2026-09-15)

Canonical: `.agent/queues/captain-objectives-2026-09-15.md`

1. **Learning Run** — NS-SKILL-003 — **IN PROGRESS**
2. **routing** — OVA-45 — awaiting Captain dispatch approval
3. **B4 — Repair loop** — **implementing** (Captain approved)

## In flight (Captain-directed)

- **M32 / B4** Captain-approved — hermetic repair CLI + evidence; awaiting PR merge
- NS-SKILL-003 / OVA-45 remain parallel queue items (dispatch still gated)

## Completed

- **M31** merged — finding outcomes → Experience → proposal-only RoutingProposal; tagged **v1.34.0**
  ([PR #152](https://github.com/loganware05/captains-compass-cursor/pull/152))
- **M30** merged — opt-in GitHub draft reviews; tagged **v1.33.0**
- **M29**–**M27** Code Reviewer track shipped
- v1.5.0–v1.34.0 / M1–M31

## Blockers

None for B4 soft stop. Await Captain merge of the M32 PR before tagging v1.35.0.
OVA-45 still needs `I approve the dispatch` for live routing.
