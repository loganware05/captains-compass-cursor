# Budget — b5-precision-ledger

| Field | Value |
|---|---|
| Plan | b5-precision-ledger |
| Status | **closed** (shipped v1.36.0) |
| Started | 2026-09-15 |
| Closed | 2026-09-16 |
| Soft stop | AC met + tests green + evidence + PR — **met** |
| Hard stop | No auto-apply reputation; no model in CI default; Linear never approves — **held** |

## Locks

1. Captain plan gate before product implementation — **satisfied**
2. Proposal-only confidence / invocation-priority deltas
3. Finding outcomes never originate Captain approval
4. Hermetic default path
5. Skill slug `code-reviewer` unchanged

## Iteration log

| When | Note |
|---|---|
| 2026-09-15 | Plan drafted on M32 closeout PR; awaiting approval |
| 2026-09-15 | Captain approved; rollback tag created; implementation on `cursor/m33-b5-precision-ledger-3b10` |
| 2026-09-15 | Hermetic tests + doctor + fixture dashboard evidence green |
| 2026-09-16 | Merged PR #160 (+ closeout #159); tagged **v1.36.0**; budget closed |
