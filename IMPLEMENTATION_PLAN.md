# Implementation Plan — M48 / Instruction Registry + Prompt Composer

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m48-instruction-registry` |
| Approved | 2026-10-01 — Captain: "I approve" + open-question answers |
| Linear | [OVA-60](https://linear.app/ovaltechnologysolutions/issue/OVA-60/m48-instruction-registry-prompt-composer-v1480) · Milestone **M48 — Instruction Registry + Prompt Composer** |
| Spec source | [Notion: Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M48 section) |
| Notion plan mirror | [M48 Implementation Plan](https://app.notion.com/p/3ece6a901c43811c8c11ee59ccf913ba) |
| Prerequisite | **M47 merged** — PR [#185](https://github.com/loganware05/captains-compass-cursor/pull/185) → `main` @ `402573e` (v1.47.0); OVA-59 Done |
| Supersedes | — (consumes M47 candidates; no Policy activation / live prompt injection) |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.47.0** @ `402573e` |
| Prepared | 2026-10-01 |
| Proposed release | **v1.48.0** (registry + composer; proposal-only; hermetic CI default) |
| Rollback | Tag `rollback/pre-m48-instruction-registry` @ `402573e` (create after approval) |
| Proposed branch | `cursor/m48-instruction-registry-plan-3192` |
| Captain | Logan Ware |

## Request

After M47 proposal-only pattern learning, establish **M48 Instruction Registry +
Prompt Composer**: a governed registry of behavioral instructions and a
PICCO-like composer that produces reproducible prompt bundles — without
activating Policies, writing live `.cursor/` guidance, or granting authority.

## Problem Statement

M47 emits `bcand-*` behavioral-guidance candidates, but NorthStar cannot yet:

1. Store versioned instructions with provenance, scope, and approval state
2. Compose Persona / Instructions / Context / Constraints / Output bundles
3. Produce stable `prompt_bundle_hash` values (schema hook exists; producers empty)
4. Expose a stable `northstar instructions` operator surface

Without this, M49 prompt evaluation and M50 Policy promotion have no registry
or composed-bundle layer to consume.

## Desired Outcome

```
M47 patterns/candidates (+ seed templates)
  → instruction registry (.agent/evaluations/behavior/instructions/)
  → PICCO composer → prompt bundles + prompt_bundle_hash
  → northstar instructions …
  → evaluate records prompt_bundle_hash (record-only)
```

No path may activate Policies, mutate `.cursor/rules|skills|agents`, mutate
Skills/routing, or set `approved_for_execution`.

## Decision Summary

| Principle | Implication |
|---|---|
| Proposal only | Draft instructions / bundles never auto-activate into live prompts |
| Separate from Skills | Capability (Skills) ≠ behavior (Policies/instructions) |
| PICCO contract | Composer emits Persona, Instructions, Context, Constraints, Output |
| Provenance | Each entry carries evidence refs, source candidate/pattern ids, version |
| Enable flag | `COMPASS_INSTRUCTIONS_ENABLED` (default off) **and** explicit CLI |
| Registry root | `.agent/evaluations/behavior/instructions/` (under behavior) |
| M47 intake | `draft-from-candidates` included in M48 |
| Evaluate wire | Record `prompt_bundle_hash` on evaluate (no live prompt injection) |
| Deterministic CI | Compose from fixtures; no network required |
| Fail closed | Missing registry / invalid entry → no bundle; never mutate authority |

## Resolved Decisions (Captain — 2026-10-01)

| # | Decision |
|---|---|
| 1 | **Both:** `COMPASS_INSTRUCTIONS_ENABLED` (default off) **and** explicit `northstar instructions` CLI |
| 2 | Registry under **`.agent/evaluations/behavior/instructions/`** |
| 3 | Release naming **confirmed: v1.48.0** |
| 4 | **Include** M47 `draft-from-candidates` in M48 |
| 5 | **Wire** `prompt_bundle_hash` into evaluate in M48 (record-only) |

## Scope

### In (M48)

1. `instruction.schema.json` + `prompt-bundle.schema.json`
2. Registry layout under `.agent/evaluations/behavior/instructions/`
3. Deterministic PICCO composer → bundle JSON + content hash
4. Draft instruction proposals from M47 `bcand-*` candidates
5. Persist bundles under `…/instructions/bundles/`
6. `northstar instructions` CLI: `list`, `show`, `compose`, `draft-from-candidates`, `export`
7. Enable gate: `COMPASS_INSTRUCTIONS_ENABLED` (default off) **and** explicit CLI
8. Wire `prompt_bundle_hash` on `northstar evaluate` (record-only)
9. Hermetic fixtures + unit/integration tests
10. Docs: ADR-065, TESTING, PROGRESS, CHANGELOG, VERSION → 1.48.0
11. Evidence under `.agent/evidence/m48-instruction-registry/`

### Out (Non-Goals)

- Live activation into `.cursor/rules|skills|agents` (M50)
- Prompt evaluation harness / regression scoring (M49)
- Policy promotion / shadow apply / Active→Proven lifecycle (M50)
- Project Overseer (M51)
- Mutating Skills, routing, reputation, or Captain approval
- Database / Prisma / frontend

## Proposed Architecture

```
scripts/northstar instructions …
        │
        ▼
scripts/run-instructions.sh
        │
        ▼
orchestrator/behavior/instructions/
  registry.py / store.py / composer.py / draft.py / service.py
        │
        ▼
.agent/evaluations/behavior/instructions/
  registry.json
  global/  agents/  task-types/  models/
  proposals/  bundles/
```

## Acceptance Criteria

- [x] Registry can list/show validated instruction entries
- [x] Composer produces deterministic PICCO bundles + stable `prompt_bundle_hash`
- [x] Drafts from M47 candidates stay `approval_state: draft` / `approved_for_execution: false`
- [x] `northstar instructions` requires enable flag + explicit CLI
- [x] Evaluate records `prompt_bundle_hash` when a bundle resolves (record-only)
- [x] Hermetic CI; no network; doctor/tests green *(validate before merge)*
- [x] No write to `.cursor/rules|skills|agents`; no Skill/routing/Policy activation
- [x] M46 evaluate + M47 learn paths still pass
- [x] Secrets never enter instruction/bundle artifacts

## Rollback Plan

1. Unset `COMPASS_INSTRUCTIONS_ENABLED`; stop using `northstar instructions`
2. Checkout `rollback/pre-m48-instruction-registry`
3. Delete `.agent/evaluations/behavior/instructions/` if needed (M46/M47 ledgers intact)

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-01 |
| Approval text | "I approve" + answers 1–5 |
| Approved revision | under-behavior registry, draft-from-candidates, evaluate hash wire, v1.48.0 |
