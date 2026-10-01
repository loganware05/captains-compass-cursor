# Autonomy Budget — m49-prompt-evaluation-harness

| Field | Value |
|---|---|
| Plan ID | `m49-prompt-evaluation-harness` |
| Phase | Planning (AWAITING APPROVAL) |
| Prepared | 2026-10-01 |

## Limits (post-approval)

| Resource | Soft | Hard |
|---|---|---|
| Implementation iterations | 3 | 5 |
| Adversarial repair rounds | 2 | 3 |
| Test suite full runs | 4 | 8 |

## Stop conditions

- Captain rejects plan or open questions block progress
- Hard iteration/cost limit reached → Budget Stop Report under `.agent/evidence/`
- Scope expansion toward M50 activation without explicit approval

## Notes

Planning-only turn: no product implementation files modified.
