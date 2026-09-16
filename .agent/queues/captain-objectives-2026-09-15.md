# Captain objective queue — 2026-09-15

Captain utterance: `Add the following objectives to queue, then begin working. Learning Run / routing / B4`

Approvals include M31/B4, B5, C1, and C2 plan approvals (2026-09-15 / 2026-09-16).

| # | Objective | Status | Binding refs |
|---|---|---|---|
| 1 | **Learning Run** — complete NS-SKILL-003 (OVA-34) | **IN PROGRESS** — awaiting OVA-47 retain | Linear [OVA-34](https://linear.app/ovaltechnologysolutions/issue/OVA-34) |
| 2 | **routing** — OVA-45 agent routing + M26 wakeability | **DISPATCHED** | [OVA-45](https://linear.app/ovaltechnologysolutions/issue/OVA-45) |
| 3 | **B4 — Repair loop** | **SHIPPED** (M32 / v1.35.0) | [OVA-48](https://linear.app/ovaltechnologysolutions/issue/OVA-48) |
| 4 | **B5 — Precision ledger** | **SHIPPED** (M33 / v1.36.0) | [OVA-49](https://linear.app/ovaltechnologysolutions/issue/OVA-49) |
| 5 | **C1 — Single launcher UX** | **SHIPPED** (M34 / v1.37.0) | [OVA-50](https://linear.app/ovaltechnologysolutions/issue/OVA-50); PRs [#162](https://github.com/loganware05/captains-compass-cursor/pull/162)/[#163](https://github.com/loganware05/captains-compass-cursor/pull/163) |
| 6 | **C2 — Product-repo install** | **IMPLEMENTING** (M35 / v1.38.0; product PR needs Captain push) | [OVA-51](https://linear.app/ovaltechnologysolutions/issue/OVA-51); [issue #164](https://github.com/loganware05/captains-compass-cursor/issues/164); evidence `.agent/evidence/c2-product-repo-install/` |

## Authority

- GitHub/repo evidence canonical; Linear records only
- Track B complete; C1 shipped
- C2 never copies control scripts; memory docs preserved
- `approved_for_execution` remains **false**

## Start order

1. Finish NS-SKILL-003 → OVA-47 retain (parallel)
2. Pause for Captain approval of C2 / `c2-product-repo-install`
3. After C2: consider C3 or Learning Run closeout

## Notes

- M34 (C1) merged as v1.37.0 ([PR #163](https://github.com/loganware05/captains-compass-cursor/pull/163))
- One Learning Run at a time — do **not** open NS-SKILL-004 until OVA-34 closes
