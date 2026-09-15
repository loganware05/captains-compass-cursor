# Budget — b4-repair-loop

| Field | Value |
|---|---|
| Plan | b4-repair-loop |
| Status | implementing |
| Started | 2026-09-15 |
| Soft stop | AC met + tests green + evidence + PR |
| Hard stop | No auto-merge; no unverified repair; no model in CI default |

## Locks

1. Verified findings only
2. Draft PR / human review — never auto-merge
3. Captain gates before dispatch and before merge
4. Linear never approves
5. Skill slug `code-reviewer` unchanged

## Iteration log

| When | Note |
|---|---|
| 2026-09-15 | Draft parked under `docs/plans/B4_REPAIR_LOOP.md` (PR #153) |
| 2026-09-15 | Promoted to root IMPLEMENTATION_PLAN after M31 closeout; awaiting Captain approval |
| 2026-09-15 | Captain approved (“I approve Implementation_Plan.md for B4 repair”); implementing |
| 2026-09-15 | Hermetic repair module/CLI/tests/evidence green; VERSION 1.35.0 |
| 2026-09-15 | Adversarial follow-up: product-allowlist-only prepare_pr; expired-agent + github-allowlist tests; code-reviewer Skill link |
