> **APPROVED / IMPLEMENTING** (2026-10-01) — Captain approved; product impl in progress.
> Active root plan: `IMPLEMENTATION_PLAN.md` (Plan ID `m48-instruction-registry`).

# M48 — Instruction Registry + Prompt Composer

Spec source: [Notion — Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M48 section)

Linear: [OVA-60](https://linear.app/ovaltechnologysolutions/issue/OVA-60/m48-instruction-registry-prompt-composer-v1480)

Notion plan mirror: [M48 Implementation Plan](https://app.notion.com/p/3ece6a901c43811c8c11ee59ccf913ba)

Prerequisite: M47 merged (#185 / v1.47.0).

## One-line summary

Governed instruction registry + PICCO prompt composer via `northstar instructions`
— proposal-only; no Policy/Skill/`.cursor/` activation.

## Baseline

v1.47.0 @ `402573e` → release **v1.48.0**

## Resolved decisions

1. `COMPASS_INSTRUCTIONS_ENABLED` + CLI
2. Registry under `.agent/evaluations/behavior/instructions/`
3. v1.48.0
4. Include `draft-from-candidates`
5. Wire `prompt_bundle_hash` into evaluate (record-only)

## Operator surface

```bash
COMPASS_INSTRUCTIONS_ENABLED=1 ./scripts/northstar instructions list --repo .
COMPASS_INSTRUCTIONS_ENABLED=1 ./scripts/northstar instructions compose --agent implementation-agent --repo .
COMPASS_INSTRUCTIONS_ENABLED=1 ./scripts/northstar instructions draft-from-candidates --repo .
```
