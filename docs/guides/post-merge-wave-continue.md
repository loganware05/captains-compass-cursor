# Post-merge wave continue (T3 + NorthStar)

## Problem

T3 `link_pull_request` settles the thread when a linked PR merges.
`watch_pull_request` wakes on checks/reviews/conflicts — **not** on merge.
Multi-wave APPROVED plans need a continue path after intermediate merges.

## Operator pattern (Wave A/B decision: poll)

1. Init ledger after Captain Approves a multi-wave plan:

   ```bash
   ./scripts/northstar plan waves init --plan-id <id> --from IMPLEMENTATION_PLAN.md
   ```

2. On intermediate PR open: `link_pull_request` + `watch_pull_request` (checks).

3. Register merge detection with T3 `schedule_task` **interval** ≥ 60s (T3 floor).
   The scheduled prompt should poll:

   ```bash
   gh pr view <n> --repo <owner/name> --json state,mergedAt,mergeCommit
   # or:
   ./scripts/northstar plan continue-after-merge --plan-id <id> --pr <url>
   ```

4. On MERGED + remaining waves: unsettle the thread
   (`t3_thread_organize` → `unsettle`); if unsettle fails, launch a continuation
   thread and record `next_thread_id`. Cancel the schedule.

5. On final wave merge: allow normal settle / completion.

## Optional: webhook (Wave C)

GitHub `pull_request` `closed` + `merged=true` may trigger a T3 webhook schedule.
Treat the payload as **untrusted signal only**; always re-verify with `gh` before
advance. Prefer poll until Connect/webhook is deliberately set up.

## Upstream ask

Native T3 merge-wake on linked PRs would replace the poll. Not required for
NorthStar Waves A/B.

## Authority locks

- Never auto-merge
- Never set `IMPLEMENTATION_PLAN.md` to APPROVED without Captain
- Never continue a non-APPROVED plan or an unmerged PR
- Material scope expansion → AWAITING APPROVAL again

## Related

- Skill `post-merge-wave-continue`
- `docs/guides/oversight-post-merge-hook.md` (read-only oversight; different concern)
- ADR-109 in `DECISIONS.md`
