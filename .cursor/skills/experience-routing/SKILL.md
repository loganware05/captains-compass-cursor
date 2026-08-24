---
name: experience-routing
description: Proposes Skill confidence and matcher weight adjustments from Experiences (proposal-only)
---

# Experience Routing

## Use this Skill when

Closing a workstream with Experiences available, or when the Captain asks for
routing improvements based on historical outcomes.

## Inputs

- One or more Experience JSON files (fixtures or `.agent/experience/`)
- Optional notes

## Procedure

1. Collect Experience paths (prefer committed fixtures for reproducible proposals).
2. Generate a **proposal-only** routing artifact:

   ```bash
   ./scripts/propose-experience-routing.sh \
     --experiences tests/fixtures/experience/contact-counter.json
   ```

3. Confirm `auto_apply` is `false` — **never** mutate `orchestrator/matcher/score.py`
   WEIGHTS from this Skill in M3.
4. Present skill confidence deltas and weight suggestions to the Captain.
5. Optionally record subagent proficiency metadata after Skill training (still
   Captain-gated):

   ```bash
   ./scripts/record-agent-proficiency.sh \
     --agent-id compass-evaluator \
     --classifications evaluation,arbitration \
     --skills compass-evaluator,execution-telemetry \
     --level developing \
     --captain-approved false
   ```

   Set `--captain-approved true` only after explicit Captain approval.

## Output

- Routing proposal under `.agent/routing/proposals/`
- Optional proficiency draft under `.agent/agents/proficiency/`

## Prohibited actions

- Do not auto-apply matcher weights
- Do not mark proficiency `captain_approved: true` without Captain confirmation
- Do not advance candidates past `SANDBOX_TESTED`
