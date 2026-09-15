# Captain objective queue — 2026-09-15

Captain utterance: `Add the following objectives to queue, then begin working. Learning Run / routing / B4`

Approvals (2026-09-15): `I've merged sanbox #57. I approve the dispatch, I approve M31/ B4 plan`; `I approve IMPLEMENTATION_PLAN.md for b5-precision-ledger`

| # | Objective | Status | Binding refs |
|---|---|---|---|
| 1 | **Learning Run** — complete NS-SKILL-003 (OVA-34) | **IN PROGRESS** — exec+Experience done; awaiting OVA-47 | Sandbox [PR #56](https://github.com/loganware05/captain-compass-sandbox/pull/56) / [#57](https://github.com/loganware05/captain-compass-sandbox/pull/57); exec branch `cursor/ova-45-ns-skill-003-exec-05fd`; Linear [OVA-34](https://linear.app/ovaltechnologysolutions/issue/OVA-34) |
| 2 | **routing** — OVA-45 agent routing + M26 wakeability | **DISPATCHED** (Captain approved) | [OVA-45](https://linear.app/ovaltechnologysolutions/issue/OVA-45) |
| 3 | **B4 — Repair loop** — FIND→PROVE→FIX→TEST→SUBMIT | **SHIPPED** (M32 / v1.35.0) | [OVA-48](https://linear.app/ovaltechnologysolutions/issue/OVA-48); [issue #154](https://github.com/loganware05/captains-compass-cursor/issues/154); PRs [#156](https://github.com/loganware05/captains-compass-cursor/pull/156)/[#157](https://github.com/loganware05/captains-compass-cursor/pull/157) |
| 4 | **B5 — Precision ledger** — Skill/reviewer reputation | **IMPLEMENTING** (M33 / v1.36.0) | [OVA-49](https://linear.app/ovaltechnologysolutions/issue/OVA-49); [issue #158](https://github.com/loganware05/captains-compass-cursor/issues/158); branch `cursor/m33-b5-precision-ledger-3b10` |

## Authority

- GitHub/repo evidence canonical; Linear records only
- `approved_for_execution` remains **false**
- B4 never auto-merges; verified findings only; sandbox/allowlist first
- B5 never auto-applies reputation / invocation priority
- M31 finding-outcomes **shipped** as [v1.34.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.34.0)
- M32 repair-loop **shipped** as [v1.35.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.35.0)

## Start order

1. Finish NS-SKILL-003 Experience → stop for OVA-47 retain
2. M33 / B5 precision ledger on control branch (parallel; proposal-only)
3. Pause for Captain merge → tag v1.36.0

## Notes

- M30 (B3) merged as v1.33.0 ([PR #149](https://github.com/loganware05/captains-compass-cursor/pull/149))
- M31 (A3) merged as v1.34.0 ([PR #152](https://github.com/loganware05/captains-compass-cursor/pull/152))
- M32 (B4) merged as v1.35.0 ([PR #156](https://github.com/loganware05/captains-compass-cursor/pull/156) / [#157](https://github.com/loganware05/captains-compass-cursor/pull/157))
- One Learning Run at a time — do **not** open NS-SKILL-004 until OVA-34 closes
