> **APPROVED / IMPLEMENTING** (2026-10-01) — Captain approved; product impl in progress.
> Active root plan: `IMPLEMENTATION_PLAN.md` (Plan ID `m49-prompt-evaluation-harness`).

# M49 — Prompt Evaluation Harness

Spec source: [Notion — Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M49 section)

Linear: [OVA-61](https://linear.app/ovaltechnologysolutions/issue/OVA-61/m49-prompt-evaluation-harness-v1490)

Notion plan mirror: [M49 Implementation Plan](https://app.notion.com/p/3ece6a901c4381cb8488e32b9b0e6634)

Prerequisite: M48 merged (#186 / v1.48.0).

## One-line summary

Hermetic baseline-vs-candidate prompt evaluation harness via `northstar prompt-eval`
— eval/proposal-only; no Policy/Skill/`.cursor/` activation.

## Baseline

v1.48.0 @ `2d388cf` → release **v1.49.0**

## Resolved decisions

1. Top-level `northstar prompt-eval`
2. New `COMPASS_PROMPT_EVAL_ENABLED` (default off)
3. Deterministic fixture scoring first
4. v1.49.0
5. Persist under `.agent/evaluations/behavior/prompt-eval/` + evidence

## Operator surface

```bash
COMPASS_PROMPT_EVAL_ENABLED=1 ./scripts/northstar prompt-eval run --repo .
COMPASS_PROMPT_EVAL_ENABLED=1 ./scripts/northstar prompt-eval compare --agent implementation-agent --repo .
COMPASS_PROMPT_EVAL_ENABLED=1 ./scripts/northstar prompt-eval export --format csv --repo .
```
