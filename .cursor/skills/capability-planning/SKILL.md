---
name: capability-planning
description: Runs the capability-aware planning pipeline and renders IMPLEMENTATION_PLAN sections
---

# Capability-Aware Planning

## Use this Skill when

The First Mate is writing or updating `IMPLEMENTATION_PLAN.md` for a non-trivial
objective and needs machine-assisted:

- required capability inference
- Skill discovery and ranking
- task graph decomposition
- agent manifest proposals

Load this Skill together with `implementation-planning` during `/plan-feature`.

## Inputs

- User objective / request text
- Repository root
- Optional context: stacks, `PROJECT_CONTEXT.md` excerpt, discovery summary
- Plan ID (defaults to `draft` until issue assigned)

## Procedure

1. Ensure registry is current: `./scripts/compile-capability-registry.sh`
2. Run the planning pipeline:

   ```bash
   ./scripts/capability-plan.sh --plan-id <plan-id> "<objective>"
   ```

3. Copy rendered sections into `IMPLEMENTATION_PLAN.md`:
   - Required Capabilities
   - Reusable Capabilities Found
   - Technology Intelligence Candidates
   - Task Graph
   - Proposed Agent Configuration
   - Evaluation Strategy
   - Learning Plan
   - Approval Boundary
4. Complete human-authored sections (Problem Statement, Acceptance Criteria, risks, etc.) using `implementation-planning`.
5. If **Capability Gaps** are present, surface them explicitly — do not silently improvise.
6. Set plan status to **AWAITING APPROVAL** and stop.

## Machine artifacts

Written under `.agent/plans/<plan-id>/`:

- `resolve.json`
- `task-graph.json`
- `manifests.json`

## Output

Capability-aware plan sections ready for Captain review.

## Prohibited actions

- Do not treat Technology Intelligence candidates as approved Skills
- Do not begin product implementation
- Do not omit capability gap sections when gaps exist
