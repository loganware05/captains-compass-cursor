> **AWAITING APPROVAL** (2026-10-01) — Plan only; no product implementation until Captain approves.
> Active root plan: `IMPLEMENTATION_PLAN.md` (Plan ID `m49-prompt-evaluation-harness`).

# M49 — Prompt Evaluation Harness

Spec source: [Notion — Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M49 section)

Linear: [OVA-61](https://linear.app/ovaltechnologysolutions/issue/OVA-61/m49-prompt-evaluation-harness-v1490)

Notion plan mirror: [M49 Implementation Plan](https://app.notion.com/p/3ece6a901c4381cb8488e32b9b0e6634)

Prerequisite: M48 merged (#186 / v1.48.0).

## One-line summary

Hermetic baseline-vs-candidate prompt evaluation harness via `northstar prompt-eval`
— proposal/eval-only; no Policy/Skill/`.cursor/` activation.

## Baseline

v1.48.0 @ `2d388cf` → proposed release **v1.49.0**

## Recommended decisions (pending Captain)

1. Top-level `northstar prompt-eval` (not nested under `instructions`)
2. New `COMPASS_PROMPT_EVAL_ENABLED` (default off)
3. Deterministic fixture scoring first
4. v1.49.0
5. Canonical reports under `.agent/evaluations/behavior/prompt-eval/` + evidence summary

## Proposed operator surface

```bash
COMPASS_PROMPT_EVAL_ENABLED=1 ./scripts/northstar prompt-eval run --repo .
COMPASS_PROMPT_EVAL_ENABLED=1 ./scripts/northstar prompt-eval compare --repo .
COMPASS_PROMPT_EVAL_ENABLED=1 ./scripts/northstar prompt-eval export --repo .
```

## Non-goals

- Policy promotion / shadow apply (M50)
- Live `.cursor/` mutation
- Live LLM scoring in CI
- Project Overseer (M51)
