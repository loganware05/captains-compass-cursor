---
name: skill-lifecycle
description: Advances candidates through APPROVED/AVAILABLE/PROVEN and tracks Skill proficiency via Experiences
---

# Skill Lifecycle

## Use this Skill when

A Technology Intelligence candidate has reached `SANDBOX_TESTED` and the Captain
wants to advance it through:

`APPROVED → AVAILABLE_SKILL → PROVEN_SKILL`

or an existing Skill should graduate toward **PROVEN** proficiency using
successful Experience evidence (training loop).

For earlier stages (`DISCOVERED → SANDBOX_TESTED`) use Skill `candidate-promotion`.

## Inputs

- Candidate JSON (staging or fixture) at `SANDBOX_TESTED` or later
- Evidence paths
- Explicit `--captain-approved` for every post-sandbox stage
- Skill slug (for AVAILABLE proposals and Experience matching)
- Experience store under `.agent/experience/` (for PROVEN)

## Procedure

1. Confirm candidate is at least `SANDBOX_TESTED` and `approved_for_execution` is false.
2. Captain-approved advance to **APPROVED**:

   ```bash
   ./scripts/promote-candidate.sh --candidate <path.json> \
     --stage APPROVED \
     --evidence .agent/evidence/approval.md \
     --captain-approved \
     --skill-slug <slug>
   ```

3. Emit **AVAILABLE_SKILL** install **proposal** (never live install):

   ```bash
   ./scripts/promote-candidate.sh --candidate <staging.json> \
     --stage AVAILABLE_SKILL \
     --evidence .agent/evidence/approval.md \
     --captain-approved \
     --skill-slug <slug>
   ```

   Review `.agent/capabilities/candidates/available-proposals/<slug>/`. Open a
   Captain-reviewed PR to copy into `.cursor/skills/<slug>/` only after approval.

4. After the Skill is used successfully in real workstreams, record Experiences
   (`execution-telemetry` / `record-execution-run.sh`) with `skills_used` including
   the slug. When **≥2** successful Experiences exist, advance to **PROVEN_SKILL**:

   ```bash
   ./scripts/promote-candidate.sh --candidate <staging.json> \
     --stage PROVEN_SKILL \
     --evidence .agent/evidence/proven.md \
     --captain-approved \
     --skill-slug <slug>
   ```

   Override threshold with `COMPASS_PROVEN_SUCCESS_THRESHOLD` if needed.

5. Optional training draft from Experience: Skill `experience-skill-training`
   (`./scripts/train-skill-from-experience.sh`).
6. Re-run `./scripts/compile-capability-registry.sh` after any live Skill PR merges.

## Output

- Staging candidate with updated `lifecycle_stage`
- AVAILABLE proposal under `.agent/capabilities/candidates/available-proposals/`
- PROVEN staging record when Experience threshold met

## Prohibited actions

- Auto-installing into `.cursor/skills/`
- Setting `approved_for_execution: true`
- Advancing past `SANDBOX_TESTED` without `--captain-approved`
- Mutating matcher weights from lifecycle advances
