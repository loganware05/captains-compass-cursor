---
name: execution-telemetry
description: Records ExecutionRun and Experience artifacts at workstream close
---

# Execution Telemetry

## Use this Skill when

Closing a workstream (`/close-workstream`), preparing a PR completion report, or
when the Captain asks to record learning from a finished plan.

## Inputs

- Plan ID
- Outcome (`success` | `partial` | `failed` | `cancelled`)
- Optional: skills used, issue, branch, PR URL, objective summary

## Procedure

1. Confirm plan status is COMPLETE (or Captain-approved stop).
2. Record telemetry from the control or product repo root:

   ```bash
   ./scripts/record-execution-run.sh \
     --plan-id <plan-id> \
     --outcome success \
     --objective "<short objective>" \
     --skills "skill-a,skill-b" \
     --issue "<issue-url>" \
     --branch "<branch>" \
     --pr "<pr-url>" \
     --repo-root <repo-root>
   ```

3. Verify artifacts under `.agent/runs/<run-id>.json` and
   `.agent/experience/<experience-id>.json`.
4. Link the Experience id in the completion report / PR body.
5. Do **not** commit product-repo Experience JSON by default (control-repo test
   fixtures only unless Captain requests otherwise).

## Output

Schema-valid ExecutionRun + Experience paths.

## Prohibited actions

- Capturing secrets, `.env` contents, or private keys in telemetry
- Auto-tuning matcher weights from Experiences (Level 3 — out of scope)
