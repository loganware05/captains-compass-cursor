# Budget — m31-finding-outcomes-experience

| Field | Value |
|---|---|
| Plan | m31-finding-outcomes-experience |
| Status | implementing |
| Started | 2026-09-15 |
| Soft stop | AC met + tests green + evidence + PR |
| Hard stop | No auto-apply RoutingProposal; no B4 repair; no model in CI |

## Locks

1. Outcomes are evidence; Captain owns any Skill confidence apply
2. Hermetic default path unchanged
3. Skill slug `code-reviewer` unchanged
4. Repair-loop deferred

## Iteration log

| When | Note |
|---|---|
| 2026-09-15 | M30 shipped (v1.33.0); M31 plan drafted; paused for Captain approval |
| 2026-09-15 | Captain approved; implementing outcomes writer + Experience/RoutingProposal |
| 2026-09-15 | Schema/module/CLI/doctor/tests/evidence green; docs + ADR-048 + VERSION 1.34.0 |
| 2026-09-15 | Hardened notes redaction for embedded token patterns; PR #152 |
| 2026-09-15 | Adversarial follow-up: proposal-notes scrub, broader patterns, empty triage guard, source_instance infer |
