---
name: candidate-promotion
description: Advances TI candidates through SANDBOX_TESTED and drafts Captain-approved Skill sidecar PRs
---

# Candidate Promotion

## Use this Skill when

A Technology Intelligence candidate should advance along:

`DISCOVERED → ANALYZED → SECURITY_REVIEWED → SANDBOX_TESTED`

or the Captain wants a **draft Skill sidecar** prepared for an approved PR into
`.cursor/skills/<slug>/`.

**M3 ceiling:** candidates stop at `SANDBOX_TESTED`. Live `APPROVED` / Skill install
still requires a Captain-approved PR. Subagent proficiency/classification is a
**separate** Captain-approved metadata path (Skill `experience-routing`).

## Inputs

- Candidate JSON path (fixture or staging)
- Target stage (`ANALYZED` default; `SECURITY_REVIEWED` / `SANDBOX_TESTED` need evidence)
- Optional target Skill slug for draft sidecar

## Procedure

1. Validate candidate (`approved_for_execution` must be false).
2. Advance lifecycle (examples):

   ```bash
   ./scripts/promote-candidate.sh --candidate <path.json>
   ./scripts/promote-candidate.sh --candidate <path.json> \
     --stage SECURITY_REVIEWED \
     --evidence .agent/evidence/security-review.md
   ./scripts/promote-candidate.sh --candidate <path.json> \
     --stage SANDBOX_TESTED \
     --evidence .agent/evidence/sandbox-test.md
   ```

3. Optionally draft a Skill sidecar proposal (still **not** live):

   ```bash
   ./scripts/promote-candidate.sh --candidate <path.json> --draft-skill <slug>
   ```

4. Open a Captain-reviewed PR to copy draft files into `.cursor/skills/<slug>/`
   only after explicit approval. Never auto-merge.
5. Re-run `./scripts/compile-capability-registry.sh` and tests after merge.
6. For **live** starred-repo discovery (Captain local only), use Skill
   `technology-intelligence-live` with `COMPASS_TI_PROVIDER=github-stars`.

## Output

- Staging candidate under `.agent/capabilities/candidates/staging/`
- Optional draft under `.agent/capabilities/candidates/skill-drafts/<slug>/`

## Prohibited actions

- Advancing candidates past `SANDBOX_TESTED` via this Skill
- Auto-installing candidates into the Skill registry
- Setting `approved_for_execution: true`
- Executing or cloning external repositories as part of promotion
