---
name: agent-skills-packaging
description: Packages and reviews agent Skills (SKILL.md + capability.yaml) using Stars-derived packaging patterns
---

# Agent Skills Packaging

## Use this Skill when

Authoring, reviewing, or promoting a NorthStar / Cursor Skill sidecar
(`SKILL.md` + `capability.yaml`), especially drafts from the Skills Learning
Loop.

## Origin

- Starred discovery: [anthropics/skills](https://github.com/anthropics/skills)
- Candidate: `github-stars-anthropics-skills`
- Lifecycle: `AVAILABLE_SKILL` (Captain-promoted Wave 1 / OVA-71)
- **Metadata/procedure only** — do not clone or execute the starred repo

## Inputs

- Draft Skill directory or Learning Loop skill-draft path
- TI scorecard evidence (security-review + dependency-supply-chain)
- Target slug and install path under `.cursor/skills/<slug>/`

## Procedure

1. Confirm the draft has YAML frontmatter (`name`, `description`) and sections:
   Use this Skill when / Inputs / Procedure / Output / Prohibited actions.
2. Ensure `capability.yaml` matches the slug, sets
   `lifecycle_stage: AVAILABLE_SKILL` (or proposal stage), and lists real
   `capabilities_provided` (not token-noise from repo names).
3. Verify M23 gates: security-review + dependency-supply-chain evidence paths
   exist; `approved_for_execution` stays false on TI candidates.
4. Register the slug in `orchestrator/registry/compiler.py` `SKILL_SLUGS`.
5. Run `./scripts/compile-capability-registry.sh` and `./scripts/doctor.sh`.
6. Ship only via Captain-reviewed PR; never auto-install from Learning Loop.

## Output

- Review notes or PR that installs `.cursor/skills/<slug>/`
- Updated capability registry compile (no warnings for the new slug)

## Prohibited actions

- Do not clone or execute external starred repositories
- Do not set `approved_for_execution: true` on TI candidates
- Do not install Skills without a Captain-reviewed PR
