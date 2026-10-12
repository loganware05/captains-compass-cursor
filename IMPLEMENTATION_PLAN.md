# Implementation Plan — M52 / Project Overseer Skill + Live StatusProvider

## Metadata

- Status: APPROVED

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m52-overseer-skill-live-provider` |
| Approved | 2026-10-11 — Captain: "I approve" (accepts recommended decisions 1–6) |
| Linear | [OVA-68](https://linear.app/ovaltechnologysolutions/issue/OVA-68/m52-project-overseer-skill-opt-in-live-statusprovider-v1570) · Project **P-OVA-4** |
| Spec source | [Notion: Persistent Project Overseer Design](https://app.notion.com/p/3eae6a901c438109ba3af1de2982826a) · post-M51 deepen |
| Notion plan mirror | [M52 Implementation Plan](https://app.notion.com/p/3f6e6a901c43815fbad0e3a43f6ba6a8) |
| Prerequisite | **M51 merged** — PR [#194](https://github.com/loganware05/captains-compass-cursor/pull/194) → **v1.56.0** @ `bf5ee25`; OVA-67 Done |
| Supersedes | Completed plan `m51-project-overseer` |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.56.0** @ `bf5ee25` |
| Prepared | 2026-10-11 |
| Proposed release | **v1.57.0** |
| Rollback | Tag `rollback/pre-m52-overseer-skill-live-provider` @ `bf5ee25` |
| Proposed branch | `feature/OVA-68-m52-overseer-skill-live-provider` |
| Capability plan | `.agent/plans/m52-overseer-skill-live-provider/` |
| Captain | Logan Ware |

## Request

Continue after M51. Behavioral Intelligence Loop M46–M51 is complete on `main`.
Deepen the Project Overseer toward the Notion design: Skill + specialist agent,
opt-in live StatusProvider, and durable system-map / scope-ledger memory —
without gaining mutating authority.

## Current state (evidence)

| Track | Reality |
|---|---|
| M46–M51 | Shipped through **v1.56.0** (#194 on `main` @ `bf5ee25`) |
| Overseer | Stub provider + hermetic drift only; no Skill/agent; no system-map |
| AHF-P07 | Explicitly deferred / gated — not this plan |
| Sprint leftovers | Prompt/policy provenance + exemplars — candidate **M53**, not this plan |

## Problem Statement

M51 proved read-oriented snapshot/explain/compare/reconcile. Operators still
lack:

1. A reusable **Project Overseer Skill** / agent profile for Cursor sessions
2. An **opt-in live model path** (Kimi/OpenRouter-shaped) for richer explanations
3. Durable **system-map** and **scope-ledger** artifacts beyond one-shot JSON snapshots
4. Explicit claim labels (**observed** / **documented** / **external** / **proposed**)

Without M52, Overseer remains a thin CLI + stub narrative.

## Desired Outcome

```
COMPASS_STATUS_ENABLED=1
[+ COMPASS_STATUS_PROVIDER=http when Captain opts in]
  → northstar status snapshot|explain|…
  → stub (CI default) OR live provider (fail-closed)
  → .agent/status/system-map.md + scope-ledger.json (proposal-safe)
  → Skill project-overseer + agent profile (advisory)
  → evidence under .agent/evidence/m52-overseer-skill-live-provider/
```

No path may approve plans, promote Skills/Policies, alter routing, merge,
deploy, or silently rewrite canonical memory docs (`PROJECT_CONTEXT.md`, etc.).

## Decision Summary (recommended)

| # | Decision | Recommendation |
|---|---|---|
| 1 | Scope | **Overseer Skill + agent + live provider + system-map/scope-ledger** (not AHF-P07, not provenance) |
| 2 | Provider gate | `COMPASS_STATUS_PROVIDER=stub\|http` (default **stub**); live never required for CI |
| 3 | Secrets | Env-only (`OPENROUTER_API_KEY` or existing approved key); never commit keys |
| 4 | Persist path | Keep **`.agent/status/`** (not design’s `.agent/state/`) |
| 5 | Memory writes | System-map / scope-ledger are Overseer artifacts; **never** auto-edit `PROJECT_CONTEXT.md` / ADRs |
| 6 | Release | **v1.57.0** |

## Resolved Decisions (Captain — 2026-10-11)

| # | Decision |
|---|---|
| 1 | Overseer Skill + agent + live provider + system-map/scope-ledger |
| 2 | `COMPASS_STATUS_PROVIDER=stub|http` (default stub) |
| 3 | Secrets via env only |
| 4 | Persist under `.agent/status/` |
| 5 | Never auto-rewrite canonical memory docs |
| 6 | Release **v1.57.0** |

## Approval Record

Captain Logan Ware — 2026-10-11 — "I approve" (recommended decisions 1–6 accepted).

## Scope

### In (M52)

1. Skill `.cursor/skills/project-overseer/SKILL.md` (+ capability sidecar if required by sync)
2. Agent profile `.cursor/agents/project-overseer.md` (advisory; cite evidence; no authority)
3. Provider protocol + `stub` (existing) + `http` adapter (OpenRouter-compatible chat completions; model configurable via env)
4. Selector: `COMPASS_STATUS_PROVIDER` default stub; fail closed to stub/error without mutating state
5. Durable artifacts under `.agent/status/`:
   - `system-map.md` (generated, clearly labeled non-canonical)
   - `scope-ledger.json` (schema-validated; proposal-safe)
6. Claim labeling on findings/explanations where practical
7. Hermetic tests: stub path unchanged; http adapter mocked (no live network in CI)
8. Doctor smoke: provider unset/stub; live path not required
9. Docs: ADR-074, TESTING, PROGRESS, PROJECT_CONTEXT (Skill count → 44), CHANGELOG, VERSION → 1.57.0
10. Evidence under `.agent/evidence/m52-overseer-skill-live-provider/`

### Out (Non-Goals)

- Live Kimi required in CI / GitHub Actions scheduled overseer
- Auto-apply reconcile to memory docs
- Cursor Cloud Automations / GH Actions post-merge trigger (docs-only mention OK)
- Prompt/policy execution provenance ledger (defer **M53**)
- Positive/negative exemplar store (defer with M53 or later)
- AHF-P07 / live trading enablement
- Changing M50 Policy Active compose gates

## Proposed Architecture

```
scripts/northstar status …
        │
        ▼
orchestrator/status/
  providers/
    stub.py          # CI / default
    http.py          # opt-in live (OpenRouter-compatible)
    select.py        # COMPASS_STATUS_PROVIDER
  memory.py          # system-map + scope-ledger writers (status tree only)
        │
        ▼
.agent/status/{snapshots,reconcile-proposals,system-map.md,scope-ledger.json}
.cursor/skills/project-overseer/
.cursor/agents/project-overseer.md
```

### Operator surface (unchanged commands; richer explain)

```bash
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
COMPASS_STATUS_ENABLED=1 COMPASS_STATUS_PROVIDER=http \
  COMPASS_STATUS_MODEL=<model> \
  ./scripts/northstar status explain --repo .
```

## Capability / Agent Plan (adjusted)

Capability planner emitted a generic graph; **override** Skills toward
`repository-discovery`, `testing-validation`, `security-review`,
`implementation-planning` — no Docker/frontend.

| Task | Profile | Notes |
|---|---|---|
| discovery | `repository-scout` | Status package + Skill/agent conventions |
| architecture | `architecture-agent` | Provider contract + memory schemas |
| implementation | `implementation-agent` | Skill/agent/provider/memory |
| validation | `test-engineer` | Hermetic + mocked http |
| documentation | `documentation-agent` | ADR/PROGRESS/VERSION |

Machine artifacts: `.agent/plans/m52-overseer-skill-live-provider/`.

## Files to Add / Modify

### Add

| Path | Purpose |
|---|---|
| `.cursor/skills/project-overseer/` | Overseer Skill |
| `.cursor/agents/project-overseer.md` | Specialist profile |
| `orchestrator/status/providers/http.py` | Opt-in live provider |
| `orchestrator/status/providers/select.py` | Provider selector |
| `orchestrator/status/memory.py` | system-map + scope-ledger |
| `orchestrator/schemas/scope-ledger.schema.json` | Ledger contract |
| `tests/orchestrator/test_m52_overseer_skill_live_provider.py` | Hermetic tests |
| `docs/plans/M52_OVERSEER_SKILL_LIVE_PROVIDER.md` | Plan archive |
| `.agent/budgets/m52-overseer-skill-live-provider.md` | Autonomy budget |
| `.agent/evidence/m52-overseer-skill-live-provider/` | Validation evidence |

### Modify (thin)

| Path | Change |
|---|---|
| `orchestrator/status/explain.py` / `snapshot.py` / `service.py` | Provider select + memory hooks |
| `orchestrator/schemas/validate.py` | Register scope-ledger schema |
| `scripts/doctor.sh` | Layout / fail-closed smoke |
| `TESTING.md`, `CHANGELOG.md`, `PROGRESS.md`, `PROJECT_CONTEXT.md`, `DECISIONS.md`, `VERSION` | M52 docs/release |
| Sidecar sync if required | Skill count / registry |

## Acceptance Criteria

- [x] Project Overseer Skill + agent profile land and are advisory-only
- [x] Default provider remains stub; CI needs no network/keys
- [x] Opt-in `COMPASS_STATUS_PROVIDER=http` uses env secrets; failure fails closed
- [x] system-map + scope-ledger written under `.agent/status/` only
- [x] Schemas reject `approved_for_execution: true` / authority mutation
- [x] No Skill/Policy/routing/plan-approval mutation; no auto memory-doc rewrite
- [x] Doctor/tests green
- [x] Evidence + ADR-074 + VERSION 1.57.0
- [x] Linear OVA-68 linked

## Test Matrix

| Layer | Coverage |
|---|---|
| Unit | Provider select, http mock, scope-ledger schema locks |
| Integration | CLI explain with stub; mocked http path |
| Regression | M51 suite unchanged green |
| Security | No secrets in artifacts; fail closed without keys |
| Doctor | Status still fail-closed when `COMPASS_STATUS_ENABLED` unset |

## Rollback Plan

1. Tag `rollback/pre-m52-overseer-skill-live-provider` @ `bf5ee25` after approval
2. Revert M52 PR / reset to tag
3. Remove Skill/agent + status memory artifacts if needed
4. VERSION / docs roll back with the revert

## Autonomy Budget

| Limit | Value |
|---|---|
| Max iterations | 8 |
| Max wall time | 4 hours |
| Stop on | Illegal authority mutation, secret leakage, budget exhaustion |

Track in `.agent/budgets/m52-overseer-skill-live-provider.md`.

## Security Considerations

- Dual gates: `COMPASS_STATUS_ENABLED` + provider select
- Secrets only via environment
- Live responses redacted before persist
- Fail closed on provider/network/schema errors
- Overseer Skill must not instruct agents to bypass Captain gates

## Approval Boundary

**Approved.** Implementation may proceed on `feature/OVA-68-m52-overseer-skill-live-provider`
with rollback `rollback/pre-m52-overseer-skill-live-provider` @ `bf5ee25`.
