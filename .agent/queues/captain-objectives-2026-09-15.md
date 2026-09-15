# Captain objective queue — 2026-09-15

Captain utterance: `Add the following objectives to queue, then begin working. Learning Run / routing / B4`

| # | Objective | Status | Binding refs |
|---|---|---|---|
| 1 | **Learning Run** — complete NS-SKILL-003 (OVA-34) | **IN PROGRESS** | Sandbox [PR #56](https://github.com/loganware05/captain-compass-sandbox/pull/56); Linear [OVA-34](https://linear.app/ovaltechnologysolutions/issue/OVA-34) |
| 2 | **routing** — OVA-45 agent routing + M26 wakeability | **IN PROGRESS** (scored; awaiting dispatch) | [OVA-45](https://linear.app/ovaltechnologysolutions/issue/OVA-45) |
| 3 | **B4 — Repair loop** — FIND→PROVE→FIX→TEST→SUBMIT | QUEUED — plan awaiting approval | [OVA-48](https://linear.app/ovaltechnologysolutions/issue/OVA-48); [issue #154](https://github.com/loganware05/captains-compass-cursor/issues/154); `IMPLEMENTATION_PLAN.md` (`b4-repair-loop`) |

## Authority

- GitHub/repo evidence canonical; Linear records only
- `approved_for_execution` remains **false**
- No B4 product implementation until Captain approves `IMPLEMENTATION_PLAN.md` for `b4-repair-loop`
- Learning Run dispatch still requires Captain: `I approve the dispatch`
- M31 finding-outcomes **shipped** as [v1.34.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.34.0) ([PR #152](https://github.com/loganware05/captains-compass-cursor/pull/152))

## Start order

1. Land / continue NS-SKILL-003 Learning Run (merge path for #56 + OVA-45 routing score)
2. Complete routing gate (stop before dispatch without Captain)
3. Await Captain approval of `b4-repair-loop` before any repair implementation

## Notes

- M30 (B3) merged as v1.33.0 ([PR #149](https://github.com/loganware05/captains-compass-cursor/pull/149))
- M31 (A3) merged as v1.34.0 ([PR #152](https://github.com/loganware05/captains-compass-cursor/pull/152))
- One Learning Run at a time — do **not** open NS-SKILL-004 until OVA-34 closes
