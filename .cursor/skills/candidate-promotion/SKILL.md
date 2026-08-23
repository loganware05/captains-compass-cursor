---
name: candidate-promotion
description: Advances TI candidates to ANALYZED and drafts Captain-approved Skill sidecar PRs
---

# Candidate Promotion

## Use this Skill when

A Technology Intelligence candidate should move from `DISCOVERED` to `ANALYZED`,
or the Captain wants a **draft Skill sidecar** prepared for an approved PR into
`.cursor/skills/<slug>/`.

## Inputs

- Candidate JSON path (fixture or staging)
- Optional target Skill slug for draft sidecar

## Procedure

1. Validate candidate (`approved_for_execution` must be false).
2. Advance to ANALYZED staging:

   ```bash
   ./scripts/promote-candidate.sh --candidate <path.json>
   ```

3. Optionally draft a Skill sidecar proposal (still **not** live):

   ```bash
   ./scripts/promote-candidate.sh --candidate <path.json> --draft-skill <slug>
   ```

4. Open a Captain-reviewed PR to copy draft files into `.cursor/skills/<slug>/`
   only after explicit approval. Never auto-merge.
5. Re-run `./scripts/compile-capability-registry.sh` and tests after merge.

## Output

- Staging candidate under `.agent/capabilities/candidates/staging/`
- Optional draft under `.agent/capabilities/candidates/skill-drafts/<slug>/`

## Prohibited actions

- Auto-installing candidates into the Skill registry
- Setting `approved_for_execution: true`
- Executing or cloning external repositories as part of promotion
