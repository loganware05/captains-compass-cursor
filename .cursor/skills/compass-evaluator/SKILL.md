---
name: compass-evaluator
description: Runs bounded evaluation experiments comparing technical alternatives
---

# Compass Evaluator

## Use this Skill when

The Captain or First Mate needs a **bounded comparison** of alternatives (A/B),
architecture options, or experiment spikes — without expanding into product
implementation.

## Inputs

- Plan ID
- Objective / question under evaluation
- At least two alternatives (id + label)
- Recommendation text
- Optional winner alternative id, hypothesis, evidence paths

## Procedure

1. Confirm the evaluation is informational — it does **not** approve product edits.
2. Record the experiment:

   ```bash
   ./scripts/run-evaluation.sh \
     --plan-id <plan-id> \
     --objective "<question>" \
     --alternatives '[{"id":"a","label":"Option A"},{"id":"b","label":"Option B"}]' \
     --recommendation "<recommendation>" \
     --winner a
   ```

3. Store evidence under `.agent/evidence/<plan-id>/` when applicable.
4. Present the evaluation id and recommendation to the Captain.
5. If a disagreement is high-cost or security-sensitive, escalate with alternatives.

## Companion subagent

Cursor subagent `compass-evaluator` may be invoked for the same procedure when
the First Mate wants a dedicated evaluation pass. Proficiency for this agent is
tracked separately via Skill `experience-routing` / `record-agent-proficiency.sh`
with **Captain-approved** metadata.

## Output

Schema-valid Evaluation JSON under `.agent/evaluations/` (gitignored runtime files).

## Prohibited actions

- Do not mutate matcher weights or Skill sidecars from an evaluation
- Do not treat evaluation winners as IMPLEMENTATION_PLAN approval
- Do not call live network Technology Intelligence as part of M3 evaluations
