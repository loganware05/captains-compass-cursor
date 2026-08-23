Close out a finished workstream after merge (or Captain decision to stop).

1. Confirm the PR is merged or the Captain explicitly abandoned the work with a recorded reason.
2. Update `PROGRESS.md`, `CHANGELOG.md` (if user-facing), and mark `IMPLEMENTATION_PLAN.md` **COMPLETE** with a completion record when appropriate.
3. Finalize the autonomy budget ledger status (COMPLETE or STOPPED).
4. Load Skill `execution-telemetry` and record an ExecutionRun + Experience:

   ```bash
   ./scripts/record-execution-run.sh \
     --plan-id <plan-id> \
     --outcome success \
     --objective "<summary>" \
     --skills "<comma-separated>" \
     --issue "<issue-url>" \
     --branch "<branch>" \
     --pr "<pr-url>" \
     --repo-root <repo-root>
   ```

5. Note rollback tag/SHA and any follow-up plans (do not start new scope without a new approved plan).
6. Recommend next action (idle, `/plan-feature` for follow-up, or sandbox refresh if this was a Compass release).
7. Reply with a short completion report only (include Experience id).
