# Evidence — M33 / B5 Precision ledger

Date: 2026-09-15  
Plan: `b5-precision-ledger` (Captain approved)  
Release target: v1.36.0  
Rollback: `rollback/pre-b5-precision-ledger`  
Issue: [#158](https://github.com/loganware05/captains-compass-cursor/issues/158)

## Artifacts

| File | What it proves |
|---|---|
| `doctor.txt` | Doctor green including precision module/schema/script |
| `unittest.txt` | `tests/orchestrator/test_m33_b5_precision_ledger.py` green |
| `precision-ledger.json` | Fixture roll-up for `b5-fixture-demo` |
| `dashboard.md` / `dashboard.json` | Per-skill precision dashboard |
| `experiences/*.json` | Per-skill Experience lessons (no blanket multi-skill success) |
| `routing-proposal.json` | Optional priority proposal (`auto_apply=false`) |
| `aggregate-result.json` | CLI summary (`captain_approval=false`) |

## Fixture precision

Source: `tests/fixtures/code-review/precision-outcomes.json`

| Skill | Accepted | Rejected | Deferred | Decided | Precision |
|---|---:|---:|---:|---:|---:|
| security-review | 4 | 1 | 0 | 5 | 80.0% |
| code-reviewer | 0 | 1 | 1 | 1 | 0.0% |

Priority proposal includes `security-review` only (meets min sample 5); `code-reviewer` omitted.

## Locks verified

- Ledger forces `captain_approval=false`
- RoutingProposal is proposal-only (`auto_apply=false`)
- Empty outcomes / empty skill keys refused
- Insufficient sample refuses priority proposal
- Deferred excluded from precision denominator
- Hermetic path — no model / no network
- Skill slug `code-reviewer` unchanged
