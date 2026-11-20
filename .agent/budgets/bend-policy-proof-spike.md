# Autonomy Budget — bend-policy-proof-spike

Status: **loop cap reached — all waves implemented; awaiting Captain review** (plan APPROVED 2026-11-18, issue #278)

| Limit | Cap | Used | Status |
|---|---:|---:|---|
| Plan iterations | 3 | 1 (+ amendments A1–A8, recorded in the plan) | held |
| Implementation loops | 8 | 8 (Wave 0, A ×2, B, review-driven hardening, harness fix-ups, docs, second-review fixes) | **cap reached — no further implementation loops without Captain approval** |
| Cost (USD) | 25 | not metered by the agent | **unverified** — Captain to confirm from billing |
| Wall time (hours) | 6 | not tracked precisely (~5 est.) | **unverified** |
| Scope | Opt-in Bend proof spike for policy lifecycle only; no production semantics change; no required dependency; no auto-approve; no auto-merge | A1 narrowed a proof claim (flagged) | held |

Loop 9 (2026-11-20) — **Captain-directed** ("Reevaluate those PRs cause both failed"): CI-only fix for
PR #279. Root cause: the `promote_policy` AST pin used `ast.dump`, whose output changed in Python 3.13,
so the lock written on 3.12 drifted on CI's 3.14. Replaced with a version-independent canonical
serializer; verified identical hashes on 3.12, 3.13 and 3.14. No scope change.

Stop and write a Budget Stop Report under `.agent/evidence/` when any limit is reached,
or when the Wave 0 feasibility gate fails. Cost and wall time are listed as unverified rather than
guessed; a stop report was not required because no metered limit is known to be exceeded.
