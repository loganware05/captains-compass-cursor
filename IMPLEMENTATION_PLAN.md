# Implementation Plan — M48 / Instruction Registry + Prompt Composer

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `m48-instruction-registry` |
| Linear | [OVA-60](https://linear.app/ovaltechnologysolutions/issue/OVA-60/m48-instruction-registry-prompt-composer-v1480) · Milestone **M48 — Instruction Registry + Prompt Composer** |
| Spec source | [Notion: Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) (M48 section) |
| Notion plan mirror | *(create with this PR)* |
| Prerequisite | **M47 merged** — PR [#185](https://github.com/loganware05/captains-compass-cursor/pull/185) → `main` @ `402573e` (v1.47.0); OVA-59 Done |
| Supersedes | — (consumes M47 candidates; no Policy activation / live prompt injection) |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.47.0** @ `402573e` |
| Prepared | 2026-10-01 |
| Proposed release | **v1.48.0** (registry + composer; proposal-only; hermetic CI default) |
| Rollback | Tag `rollback/pre-m48-instruction-registry` @ `402573e` (create after approval) |
| Proposed branch | `cursor/m48-instruction-registry-3192` *(implementation after approval; this PR is plan + M47 closeout)* |
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
M47 patterns/candidates (+ optional seed templates)
  → instruction registry (.agent/instructions/)
  → PICCO composer → prompt bundles + prompt_bundle_hash
  → northstar instructions …
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
| Enable flag | Proposed: `COMPASS_INSTRUCTIONS_ENABLED` (default off) + explicit CLI |
| Deterministic CI | Compose from fixtures; no network required |
| Separate CLI | `northstar instructions` distinct from `evaluate` / `learn` / `skills` |
| Fail closed | Missing registry / invalid entry → no bundle; never mutate authority |
| Builds on M47 | Optional intake from `bcand-*`; does not overload Skill promotion |

## Current-State Analysis (live repo @ `402573e`)

| Area | Location | M48 use |
|---|---|---|
| M47 candidates | `.agent/evaluations/behavior/patterns/candidates/` | Optional draft intake |
| Empty hash hook | `evaluator.prompt_bundle_hash` on behavior eval | Composer output target |
| Live guidance today | `.cursor/rules`, `.cursor/skills`, `.cursor/agents` | **Read-only reference; do not write** |
| Proposal analogs | routing proposals, skill candidates, persistent-role staging | Pattern for proposal-only |
| CLI launcher | `scripts/northstar` (`evaluate`, `learn`; no `instructions`) | Add `instructions` |
| Skill learning | `orchestrator/learning/` | **Do not conflate** |
| Instruction registry | **absent** | Create under `.agent/instructions/` |

### Capability-plan note

Reject any frontend/DB workstreams. M48 is control-plane Python/CLI + markdown
registry artifacts only.

## Scope

### In (M48)

1. `instruction.schema.json` + `prompt-bundle.schema.json`
2. Registry layout under `.agent/instructions/` (see architecture)
3. Deterministic PICCO composer → bundle JSON + content hash
4. Optional: draft instruction proposals from M47 `bcand-*` candidates
5. Persist bundles under `.agent/instructions/bundles/`
6. `northstar instructions` CLI: e.g. `list`, `show`, `compose`, `draft-from-candidates`, `export`
7. Enable gate: `COMPASS_INSTRUCTIONS_ENABLED` (default off) **and** explicit CLI *(open Q1)*
8. Wire `prompt_bundle_hash` when composing for a known execution context (record-only; no live prompt injection)
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
orchestrator/instructions/
  registry.py    # load/validate registry entries
  composer.py    # PICCO compose → prompt-bundle + hash
  draft.py       # optional M47 candidate → draft instruction
  store.py       # persist bundles / proposals
  enabled.py     # COMPASS_INSTRUCTIONS_ENABLED
        │
        ▼
.agent/instructions/
  registry.yaml          # index of instruction ids + paths
  global/                # operating brief, shared constraints
  agents/                # per-agent overlays
  task-types/            # implementation / research / review / planning
  models/                # model-specific rendering notes (optional)
  proposals/             # draft instructions (proposal-only)
  bundles/               # composed prompt-bundle JSON
```

### Instruction entry (conceptual)

```json
{
  "instruction_id": "instr-...",
  "scope": "agent|task-type|global|model",
  "title": "...",
  "body_path": "agents/code-reviewer.md",
  "source_candidate_ids": ["bcand-..."],
  "evidence_pattern_ids": ["bpat-..."],
  "schema_version": "1",
  "approval_state": "draft",
  "approved_for_execution": false,
  "authority_mutation": false
}
```

### Prompt bundle (conceptual)

```json
{
  "bundle_id": "pbundle-...",
  "prompt_bundle_hash": "sha256:...",
  "persona": "...",
  "instructions": ["..."],
  "context": {},
  "constraints": ["..."],
  "output": "...",
  "instruction_ids": ["instr-..."],
  "model_hint": "",
  "approved_for_execution": false,
  "authority_mutation": false
}
```

## Workstreams

| ID | Work |
|---|---|
| WS1 | Instruction + prompt-bundle schemas |
| WS2 | Registry layout + loader/validator |
| WS3 | PICCO composer + deterministic hashing |
| WS4 | Optional draft-from-M47-candidates |
| WS5 | `northstar instructions` CLI + enable flag |
| WS6 | Hermetic tests + fixtures; docs ADR-065 / VERSION 1.48.0 / doctor |

## Files Expected to Change

**New:** `orchestrator/instructions/`, schemas, `scripts/run-instructions.sh`,
`.agent/instructions/**`, tests/fixtures, `docs/plans/M48_…`, evidence dir.

**Modify:** `scripts/northstar`, `scripts/doctor.sh`, DECISIONS/TESTING/PROGRESS/CHANGELOG/VERSION,
`docs/integrations/decision-provider.md` (cross-link instructions vs evaluate/learn),
optionally thin hook to record `prompt_bundle_hash` on behavior eval when a bundle is composed.

## Acceptance Criteria

- [ ] Registry can list/show validated instruction entries from `.agent/instructions/`
- [ ] Composer produces deterministic PICCO bundles + stable `prompt_bundle_hash`
- [ ] Drafts from M47 candidates (if enabled) stay `approval_state: draft` / `approved_for_execution: false`
- [ ] `northstar instructions` requires enable flag (if approved) + explicit CLI
- [ ] Hermetic CI; no network; doctor/tests green
- [ ] No write to `.cursor/rules|skills|agents`; no Skill/routing/Policy activation
- [ ] M46 evaluate + M47 learn paths unchanged and still pass
- [ ] Secrets never enter instruction/bundle artifacts

## Testing Strategy

| Layer | What |
|---|---|
| Unit | Schema locks, hash stability, PICCO field presence |
| Integration | `northstar instructions compose` over fixture registry |
| Regression | evaluate / learn / skills untouched |
| Security | No secret leakage; proposal-only locks; no `.cursor/` writes |

## Security Review

- Read M47 candidates / seed templates only; redaction inherited
- Bundles cannot grant authority
- Enable flag default off
- Never write secrets into registry markdown or bundle JSON

## Accessibility Review

N/A (CLI / control-plane).

## Migration Plan

Additive. Empty `.agent/instructions/` until first seed/compose. Optional seed
of a minimal global operating-brief template (proposal-only). No backfill of
historical evals required.

## Rollback Plan

1. Unset `COMPASS_INSTRUCTIONS_ENABLED`; stop using `northstar instructions`
2. Checkout `rollback/pre-m48-instruction-registry`
3. Delete `.agent/instructions/` if needed (M46/M47 ledgers intact)

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Conflate with Skills Learning Loop | Separate package + CLI surface |
| Accidental `.cursor/` mutation | Hard Non-Goal + tests asserting no writes |
| Scope creep into M49/M50 | No eval harness / activation in M48 |
| Monolithic mega-prompt | PICCO sections + scoped overlays |

## Open Questions (Captain)

| # | Question | Options |
|---|---|---|
| 1 | Enable gate? | **A)** `COMPASS_INSTRUCTIONS_ENABLED` + CLI (mirror M46/M47) · **B)** CLI-only |
| 2 | Registry root? | **A)** `.agent/instructions/` (Notion layout) · **B)** under `.agent/evaluations/behavior/instructions/` |
| 3 | Release naming? | Confirm **v1.48.0** |
| 4 | M47 intake in M48? | **A)** Yes — `draft-from-candidates` · **B)** Registry+composer only; intake deferred to M50 |
| 5 | Wire `prompt_bundle_hash` into evaluate path in M48? | **A)** Record-only when bundle composed · **B)** Defer wiring to M49 |

## Assumptions

1. M47 on `main` is the candidate feed (if intake approved).
2. Proposal-only registry is sufficient for M48; activation waits for M49–M50.
3. Control repo is the implementation target.

## Definition of Done

M48 complete when NorthStar can maintain a governed instruction registry, compose
PICCO prompt bundles with stable hashes via `northstar instructions`, pass
validation with evidence, and grant **no new mutating authority**.

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

## Approval Record

| Field | Value |
|---|---|
| Approved by | — |
| Approval date | — |
| Approval text | — |
| Approved revision | — |
