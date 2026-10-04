# Progress

## Current status

**Implementing: AHF-P01 AI Hedge Fund intake + read-only adapter** —
Linear [OVA-62](https://linear.app/ovaltechnologysolutions/issue/OVA-62/ahf-p01-ai-hedge-fund-intake-read-only-northstar-adapter)
· Project [P-OVA-5](https://linear.app/ovaltechnologysolutions/project/northstar-on-chain-ai-hedge-fund-67b1475ea115).
Plan: `ahf-p01-intake-adapter` · Branch: `cursor/ahf-p01-intake-adapter-8613`.

| Item | Value |
|---|---|
| On main | **v1.49.0** M49 (#187) @ `b007dc4` |
| Active plan | `ahf-p01-intake-adapter` — **IN PROGRESS** (approved 2026-10-04) |
| Linear | [OVA-62](https://linear.app/ovaltechnologysolutions/issue/OVA-62/ahf-p01-ai-hedge-fund-intake-read-only-northstar-adapter) · [P-OVA-5](https://linear.app/ovaltechnologysolutions/project/northstar-on-chain-ai-hedge-fund-67b1475ea115) |
| Spec | [Utilization Map](https://app.notion.com/p/3efe6a901c438145aacfce97e28fc7a1) · [plan mirror](https://app.notion.com/p/3efe6a901c4381a1b7deda6bcab98cbb) |
| Release | **v1.50.0** |
| Rollback | `rollback/pre-ahf-p01-intake-adapter` @ `b007dc4` |

### Captain decisions (2026-10-04)

1. VERSION **v1.50.0**
2. Documented SHA + optional local path
3. New Linear project (also tracks `bitcoin-data-collector`)
4. AHF-P03 = separate plan on **existing `bitcoin-data-collector` repo**
5. Fixture-only strategy agents in v1

## Parallel track — On-Chain / AI Hedge Fund (AHF)

1. **AHF-P01 Intake + read-only adapter** ← implementing (OVA-62)
2. AHF-P02 Jev shadow (agent/strategy or signal triage) — deferred
3. AHF-P03 BTC on-chain metric family (`bitcoin-data-collector`) — deferred
4. AHF-P04+ On-chain analyst, portfolio experiments, behavioral feed — deferred

## Behavioral Intelligence Loop

1. ~~**M46 Behavior Intelligence Foundation**~~ merged (#184) — OVA-58 Done · v1.46.0
2. ~~**M47 Pattern learning**~~ merged (#185) — OVA-59 Done · v1.47.0
3. ~~**M48 Instruction registry + prompt composer**~~ merged (#186) — OVA-60 Done · v1.48.0
4. ~~**M49 Prompt evaluation harness**~~ merged (#187) — OVA-61 · v1.49.0
5. M50 Policy / instruction promotion (deferred; VERSION numbering resumes after AHF as needed)
6. M51 Kimi K3 Project Overseer (deferred)

## Completed recently

- **M49 → v1.49.0** — Prompt Evaluation Harness (#187)
- **M48 → v1.48.0** — Instruction Registry + Prompt Composer (#186)
- **M47 → v1.47.0** — Behavior Pattern Learning (#185)
- **M46 → v1.46.0** — Behavior Intelligence Foundation (#184)

## Blockers

None.
