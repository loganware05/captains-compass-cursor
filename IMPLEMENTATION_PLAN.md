# Implementation Plan — M53 / Prompt-Policy Provenance + Behavior Exemplars

## Metadata

- Status: APPROVED

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m53-prompt-policy-provenance` |
| Approved | 2026-10-11 — Captain: "I approve" (accepts recommended decisions 1–6) |
| Linear | [OVA-69](https://linear.app/ovaltechnologysolutions/issue/OVA-69/m53-promptpolicy-provenance-behavior-exemplars-v1580) · Project **P-OVA-4** |
| Spec source | [Notion: Behavioral Intelligence Loop Sprint](https://app.notion.com/p/3ebe6a901c4381da93c8d5abaa694107) — Provenance + Exemplars sections |
| Notion plan mirror | [M53 Implementation Plan](https://app.notion.com/p/3f7e6a901c4381569ebcf3e3d74e993d) |
| Prerequisite | **M52 merged** — PR [#195](https://github.com/loganware05/captains-compass-cursor/pull/195) → **v1.57.0** @ `448ac25`; OVA-68 Done |
| Supersedes | Completed plan `m52-overseer-skill-live-provider` |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.57.0** @ `448ac25` |
| Prepared | 2026-10-11 |
| Proposed release | **v1.58.0** |
| Rollback | Tag `rollback/pre-m53-prompt-policy-provenance` @ `448ac25` |
| Proposed branch | `feature/OVA-69-m53-prompt-policy-provenance` |
| Capability plan | `.agent/plans/m53-prompt-policy-provenance/` |
| Captain | Logan Ware |

## Request

Continue after M52. Close Behavioral Intelligence Loop sprint leftovers:
**execution provenance** (why two similar runs behaved differently) and
**positive/negative exemplars** (evidence-backed behavior worth preserving or
avoiding) — without granting new mutating authority.

## Current state (evidence)

| Track | Reality |
|---|---|
| M46–M52 | Shipped through **v1.57.0** (#195 on `main` @ `448ac25`) |
| Provenance today | Partial: `prompt_bundle_hash` on prompt bundles / some evaluations / policies; not a unified execution provenance ledger |
| Exemplars | Signal definitions mention “success exemplar”; no `.agent/examples/` store |
| AHF-P07 | Still deferred / gated |

## Problem Statement

Operators cannot yet:

1. Inspect a single provenance record tying an execution to prompt bundle,
   instructions, policies, Skills, model/provider, context route, SHA, and
   NorthStar version
2. Curate bounded positive/negative behavior exemplars with evidence refs for
   future learning / prompt-eval fixtures
3. Export those artifacts without mutating Skills, Policies, or routing

## Desired Outcome

```
execution / evaluation / compose surfaces
  → provenance record (schema-validated)
  → .agent/evaluations/behavior/provenance/<id>.json
  → optional exemplar draft under .agent/examples/{positive,negative}/
  → northstar provenance … / northstar examples …
  → evidence under .agent/evidence/m53-prompt-policy-provenance/
```

No path may approve plans, promote Skills/Policies, alter routing, merge,
deploy, or auto-activate Policies from exemplars.

## Decision Summary (recommended)

| # | Decision | Recommendation |
|---|---|---|
| 1 | Scope | **Provenance ledger + exemplar store + CLI** (not AHF-P07, not scheduled Overseer) |
| 2 | Enable gate | New `COMPASS_PROVENANCE_ENABLED` (default off) **and** explicit CLI |
| 3 | Persist | Provenance under `.agent/evaluations/behavior/provenance/`; exemplars under `.agent/examples/` |
| 4 | Wire-in | Attach/emit provenance from M46 evaluate + M48 compose when fields available (best-effort; missing fields allowed with empty strings / omitted optionals) |
| 5 | Exemplars | Proposal/read-only drafts; Captain-curated; never auto-promote |
| 6 | Release | **v1.58.0** |

## Resolved Decisions (Captain — 2026-10-11)

| # | Decision |
|---|---|
| 1 | Provenance ledger + exemplar store + CLI |
| 2 | `COMPASS_PROVENANCE_ENABLED` (default off) |
| 3 | Persist under `.agent/evaluations/behavior/provenance/` + `.agent/examples/` |
| 4 | Best-effort emit from evaluate/compose when gated |
| 5 | Exemplars never auto-promote |
| 6 | Release **v1.58.0** |

## Approval Record

Captain Logan Ware — 2026-10-11 — "I approve" (recommended decisions 1–6 accepted).

## Scope

### In (M53)

1. Schema `execution-provenance.schema.json` — required fail-closed
   `authority_mutation: false`; fields aligned to sprint list:
   `prompt_bundle_hash`, `instruction_ids`, `policy_ids`, `skill_ids` /
   skill version refs when available, `model`, `model_provider`,
   `context_route`, `repository_sha`, `northstar_version`, `execution_id`
2. Schema `behavior-exemplar.schema.json` — `polarity: positive|negative`,
   evidence refs, optional linked evaluation/provenance IDs;
   `approved_for_execution: false`
3. Package helpers under `orchestrator/behavior/provenance/` +
   `orchestrator/behavior/exemplars/`
4. Operator surface (via `scripts/northstar` + runner):
   - `northstar provenance capture|show|list|export`
   - `northstar examples list|show|draft|export`
5. Best-effort attach on `northstar evaluate run` / compose when gated on
6. Hermetic fixtures + unit/integration tests (no live providers)
7. Doctor smoke: fail-closed when provenance flag unset
8. Docs: ADR-075, TESTING, PROGRESS, PROJECT_CONTEXT, CHANGELOG, VERSION → 1.58.0
9. Evidence under `.agent/evidence/m53-prompt-policy-provenance/`

### Out (Non-Goals)

- Auto-activating Policies or rewriting Skills from exemplars
- Requiring complete provenance on every historical run (backfill optional/manual)
- Live Kimi / OpenRouter in CI
- AHF-P07 / live trading
- GitHub Actions scheduled Overseer

## Proposed Architecture

```
scripts/northstar provenance|examples …
        │
        ▼
orchestrator/behavior/provenance/   # capture + store + export
orchestrator/behavior/exemplars/    # draft + list (proposal-only)
        │
        ▼
.agent/evaluations/behavior/provenance/<prov-id>.json
.agent/examples/positive|negative/<ex-id>/exemplar.json
```

### Operator surface (proposed)

```bash
COMPASS_PROVENANCE_ENABLED=1 ./scripts/northstar provenance capture --execution-id <id> --repo .
COMPASS_PROVENANCE_ENABLED=1 ./scripts/northstar provenance list --repo .
COMPASS_PROVENANCE_ENABLED=1 ./scripts/northstar examples draft --polarity positive --evaluation-id <id> --repo .
```

## Capability / Agent Plan (adjusted)

Generic capability graph; **override** toward behavior/orchestrator Skills —
no Docker/frontend.

| Task | Profile | Notes |
|---|---|---|
| discovery | `repository-scout` | Locate evaluate/compose/packet seams |
| architecture | `architecture-agent` | Provenance + exemplar contracts |
| implementation | `implementation-agent` | Package + CLI |
| validation | `test-engineer` | Hermetic tests + doctor |
| documentation | `documentation-agent` | ADR/PROGRESS/VERSION |

Machine artifacts: `.agent/plans/m53-prompt-policy-provenance/`.

## Files to Add / Modify

### Add

| Path | Purpose |
|---|---|
| `orchestrator/schemas/execution-provenance.schema.json` | Provenance contract |
| `orchestrator/schemas/behavior-exemplar.schema.json` | Exemplar contract |
| `orchestrator/behavior/provenance/` | Capture/store/export |
| `orchestrator/behavior/exemplars/` | Draft/list/export |
| `scripts/run-provenance.sh` | Enable-gated runner |
| `tests/fixtures/behavior/provenance/` | Hermetic fixtures |
| `tests/orchestrator/test_m53_prompt_policy_provenance.py` | Tests |
| `docs/plans/M53_PROMPT_POLICY_PROVENANCE.md` | Plan archive |
| `.agent/budgets/m53-prompt-policy-provenance.md` | Autonomy budget |
| `.agent/evidence/m53-prompt-policy-provenance/` | Validation evidence |
| `.agent/examples/{positive,negative}/` layout | Exemplar roots |
| `.agent/evaluations/behavior/provenance/` layout | Provenance root |

### Modify (thin)

| Path | Change |
|---|---|
| `orchestrator/behavior/service.py` / ledger / composer | Best-effort provenance emit when gated |
| `orchestrator/behavior/enabled.py` | Provenance enable gate |
| `scripts/northstar` | Dispatch `provenance` + `examples` |
| `scripts/doctor.sh` | Fail-closed smoke |
| `orchestrator/schemas/validate.py` | Register schemas |
| Docs / VERSION | M53 release memory |

## Acceptance Criteria

- [x] Provenance schema + store + CLI behind `COMPASS_PROVENANCE_ENABLED`
- [x] Exemplar schema + draft/list/export; never auto-promotes
- [x] Evaluate/compose can emit provenance when fields available (hermetic)
- [x] Schemas reject authority mutation / approved_for_execution true
- [x] Doctor/tests green; no live providers required
- [x] Evidence + ADR-075 + VERSION 1.58.0
- [x] Linear OVA-69 linked

## Test Matrix

| Layer | Coverage |
|---|---|
| Unit | Schema locks, capture with partial fields, exemplar draft |
| Integration | CLI list/export; evaluate path emit when gated |
| Regression | M46–M52 suites green |
| Security | Fail-closed gate; no secrets in provenance/exemplars |
| Doctor | Flag unset → provenance unavailable |

## Rollback Plan

1. Tag `rollback/pre-m53-prompt-policy-provenance` @ `448ac25` after approval
2. Revert M53 PR / reset to tag
3. Remove provenance/exemplar operator artifacts if needed
4. VERSION / docs roll back with the revert

## Autonomy Budget

| Limit | Value |
|---|---|
| Max iterations | 8 |
| Max wall time | 4 hours |
| Stop on | Illegal authority mutation, secret leakage, budget exhaustion |

Track in `.agent/budgets/m53-prompt-policy-provenance.md`.

## Security Considerations

- Dual enable gate + explicit CLI
- Redact secret-like strings before persist
- Exemplars never grant execution authority
- Fail closed on malformed inputs

## Approval Boundary

**Approved.** Implementation may proceed on `feature/OVA-69-m53-prompt-policy-provenance`
with rollback `rollback/pre-m53-prompt-policy-provenance` @ `448ac25`.
