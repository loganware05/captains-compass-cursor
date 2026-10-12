---
name: goose-agent-orchestration
description: Designs agent orchestration and tool-routing procedures inspired by extensible agent runtimes
---

# Goose Agent Orchestration

## Use this Skill when

Designing multi-step agent workflows, tool routing, or runtime boundaries for
NorthStar agents — without installing third-party agent frameworks into the
control plane.

## Origin

- Starred discovery: [aaif-goose/goose](https://github.com/aaif-goose/goose)
- Candidate: `github-stars-aaif-goose-goose`
- Lifecycle: `AVAILABLE_SKILL` (Captain-promoted Wave 1 / OVA-71)
- **Metadata/procedure only** — do not clone or execute the starred repo

## Inputs

- Objective / task graph or capability plan
- Available Skills and agent profiles
- Evidence expectations for the workstream

## Procedure

1. Prefer NorthStar launcher surfaces (`northstar skills|review|evaluate|…`)
   over ad-hoc agent frameworks.
2. Map the objective to Skills + agents via capability planning / experience
   routing; keep Captain approval gates intact.
3. Define clear tool boundaries: what runs in control vs product/sandbox.
4. Require evidence paths for mutating steps; fail closed on missing gates.
5. If inspired by an external runtime pattern, capture it as a Skill/procedure
   draft — never as a live dependency install from the Star.
6. Record Experiences with `skills_used` including this slug when the pattern
   is applied successfully.

## Output

- Task/agent routing notes or capability-plan sections
- Optional Skill improvement proposal for related orchestration Skills

## Prohibited actions

- Do not clone, npm-install, or execute Goose (or similar) from TI/learning paths
- Do not bypass `IMPLEMENTATION_PLAN.md` approval for product changes
- Do not grant agents authority to self-approve promotions
