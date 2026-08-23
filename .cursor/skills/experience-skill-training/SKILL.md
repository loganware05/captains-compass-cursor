---
name: experience-skill-training
description: Imports a product-repo Experience and drafts a Skill for control-repo testing
---

# Experience Skill Training

## Use this Skill when

A **production/product** repository has an Experience sample the Captain wants
Compass to learn from. By default Experiences stay in control-repo **test fixtures**;
this Skill is the second instance that imports a product Experience into the
**control repo** for draft Skill training and local validation.

## Inputs

- Path to Experience JSON (often from a product repo `.agent/experience/`)
- Control repository root (this Compass repo)
- Optional Skill slug

## Procedure

1. Confirm the Experience validates against `experience.schema.json`.
2. Train a draft Skill in control-repo staging (not live Skills):

   ```bash
   ./scripts/train-skill-from-experience.sh \
     --experience /path/to/product/.agent/experience/<id>.json \
     --control-root /path/to/captains-compass-cursor \
     [--skill-slug my-new-skill]
   ```

3. Review drafts under
   `.agent/capabilities/candidates/skill-drafts/<slug>/`.
4. Run control-repo validation:

   ```bash
   ./scripts/doctor.sh
   PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_*.py' -q
   ```

5. If validation passes, open a **Captain-approved PR** to promote the draft into
   `.cursor/skills/<slug>/` (use `candidate-promotion` guidance). Stop for approval.

## Output

Draft `SKILL.md` + `capability.yaml` + copied source Experience in staging.

## Prohibited actions

- Writing drafts directly into `.cursor/skills/` without Captain approval
- Skipping control-repo tests
- Treating product Experiences as live Compass Skills automatically
