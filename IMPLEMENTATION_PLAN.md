# Implementation Plan

## Metadata

- Status: APPROVED
- Plan ID: m1-capability-aware-planning
- Issue: [#35](https://github.com/loganware05/captains-compass-cursor/issues/35)
- Branch: `feature/35-m1-capability-aware-planning`
- Target release: **v1.5.0** (foundational orchestration slice; non-breaking additive)
- Created: 2026-08-19
- Last updated: 2026-08-19
- Approved by: Captain
- Approval date: 2026-08-19
- Approved revision: M1 as drafted; capability metadata = sidecar `capability.yaml` (ADR-017)
- Rollback checkpoint: `rollback/pre-m1-capability-aware-planning` (`5929f10`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Meta prompt: Foundation Implementation (Milestone 1 — capability-aware planning)
  - Current repo baseline: **v1.4.0** (`a2fe6ce`)

## Request

Evolve Captain's Compass from a reusable Cursor engineering workflow into the **foundation** of a persistent, capability-aware, multi-agent project operating system — without replacing existing architecture.

**Milestone 1 scope only:** build the smallest end-to-end vertical slice that turns a vague objective into an **enhanced, approval-gated** `IMPLEMENTATION_PLAN.md` containing capability inference, Skill discovery, task graph, agent manifest proposals, and model recommendations — then **stop at the existing approval gate**.

**Explicitly out of scope for M1:**

- Autonomous product execution beyond today's post-approval machinery
- Technology Intelligence Engine implementation (GitHub Star Categorization integration body)
- Vector databases, ML routing, persistent Knowledge Steward agent
- Deleting or replacing the eight specialist subagents
- Automatic execution of external/starred repositories

## Problem Statement

Today, planning is procedural (Skill + First Mate judgment) but not **machine-assisted**:

- Skills expose only `name` + `description` frontmatter; no structured capability metadata
- Agents are static Markdown profiles with no link to required capabilities or model classes
- `IMPLEMENTATION_PLAN.md` has no standard sections for capability match, task graph, or agent manifests
- No deterministic registry, scorer, or tests for planning decisions
- No adapter boundary for future Technology Intelligence candidates

The North Star (Notion + meta prompt) requires incremental extension of what already works — not a parallel orchestration framework.

## Desired Outcome

Given a vague objective and repository context, Captain Compass can **deterministically** produce a plan artifact that explains:

1. What needs to be built and why each task exists
2. Required capabilities vs reusable Skills found (with explicit gaps)
3. Dependency-aware task graph and parallelization eligibility
4. Proposed per-task agent manifests (Skills, reference agent profile, model class, budget, rationale)
5. Git strategy, validation, risks, evaluation, and learning retention — within the existing approval gate

Success means the Captain can approve or reject planning quality **before** any product implementation begins.

## Acceptance Criteria

- [x] Minimal JSON Schemas exist for Capability, Task, AgentManifest, ModelProfile (+ stub CandidateCapability, ExecutionRun stubs for extension)
- [x] All 24 Skills are discoverable via a compiled registry (authored metadata + safe inference fallback)
- [x] Eight existing subagents are indexed as **reference agent profiles** (not deleted; extracted capabilities)
- [x] Deterministic orchestrator modules: registry load, capability inference, task decomposition, dependency validation, Skill ranking, manifest assembly, plan section rendering
- [x] Technology Intelligence **provider interface** exists with a no-op/stub provider (no GitHub Stars coupling)
- [x] Enhanced `IMPLEMENTATION_PLAN.md` template + `/plan-feature` command document new sections
- [x] New Skill `capability-planning` instructs First Mate to run the orchestrator during planning
- [x] Capability gaps surface explicitly (no silent improvisation fixture case)
- [x] `plan-approval-check.sh` behavior unchanged for APPROVED/DRAFT gating
- [x] `./scripts/doctor.sh`, `./tests/run.sh`, `./tests/evals/run.sh` pass with new tests added
- [x] Install/update propagate new orchestrator assets and registry build step where applicable
- [x] ADR-017 recorded; PROGRESS/CHANGELOG updated on completion *(CHANGELOG on v1.5.0 release)*
- [ ] No product-repo implementation changes in this milestone (control-repo only)

## Non-Goals

- Level 3 self-improvement / autonomous routing weight tuning
- Candidate Skill promotion lifecycle automation (DISCOVERED → PROVEN)
- Experience store population from live Git telemetry (schema + directory layout only)
- Evaluator experiment runner (design hook only)
- Replacing Cursor subagent invocation mechanics

## Assumptions

- Python 3 is available locally and in CI (already required by hooks)
- M1 runs in the **control repository**; product repos consume outputs via enhanced plan template + installed Skill
- Cursor model selection remains Captain/IDE-controlled; M1 recommends **model classes** and documented slugs, not live API routing
- GitHub issue creation waits until Captain approval (per workflow rules)
- Current branch `chore/32-release-v1.4.0` is not the implementation branch; work begins on a feature branch after approval

## Resolved Decisions

1. **Registry build timing:** compile on `doctor.sh` / `tests/run.sh`; do not commit compiled `registry.json` by default (generate at validate time).
2. **Sidecar vs frontmatter:** **sidecar `capability.yaml`** — accepted. See [CAPABILITY_METADATA_SIDECAR_VS_FRONTMATTER.md](docs/design/CAPABILITY_METADATA_SIDECAR_VS_FRONTMATTER.md) and ADR-017.
3. **Orchestrator CLI entrypoint:** `scripts/capability-plan.sh` wrapper calling Python module (matches existing script style).
4. **Issue:** [#35](https://github.com/loganware05/captains-compass-cursor/issues/35).

---

## Repository Discovery Summary

### Current architecture to extend (do not replace)

| Primitive | Location | Role today |
|---|---|---|
| Authority model | `AGENTS.md`, rules `00`–`04` | Captain / First Mate, approval gate |
| Planning Skill | `.cursor/skills/implementation-planning/` | Writes `IMPLEMENTATION_PLAN.md`, stops |
| Discovery Skill | `.cursor/skills/repository-discovery/` | Read-only repo report |
| Git orchestration | `.cursor/skills/worktree-orchestration/` | Branches/worktrees **after** approval |
| Phase commands | `.cursor/commands/plan-feature.md`, etc. | Thin prompts wrapping Skills |
| Specialist agents | `.cursor/agents/*.md` (8) | Static role templates |
| Skills | `.cursor/skills/*/SKILL.md` (23) | Stack/procedure knowledge |
| Hooks | `plan-approval-check.sh` (fail-closed) | Blocks product edits until APPROVED |
| Evidence | `.agent/evidence/`, budgets, sessions, runs | Validation + autonomy |
| Installer | `scripts/install.sh` | Copies `.cursor/*`, seeds `.agent/*` |
| Tests | `tests/run.sh`, `tests/evals/run.sh` | Deterministic harness sensors |

### What does not exist yet

- No `orchestrator/` module
- No capability registry or JSON Schemas
- No machine-readable task graph or agent manifest artifacts
- No Technology Intelligence provider boundary
- "Orchestration" today means **Git worktrees**, not multi-agent assembly

### Investigation task answers

1. **Extend:** rules, Skills, agents, commands, hooks, `IMPLEMENTATION_PLAN.md` template, doctor, install/update, tests/evals, `.agent/` layout.  
   **Do not replace:** approval gate, hook fail-closed policy, install memory-doc preservation.
2. **Skills today:** YAML frontmatter `{name, description}` + Markdown sections (Use when / Inputs / Procedure / Output / Prohibited).
3. **Agents today:** YAML frontmatter `{name, description}` + role instructions; Cursor subagents, not dynamic manifests.
4. **Orchestration-adjacent Skills:** `repository-discovery`, `implementation-planning`, `worktree-orchestration`, `testing-validation`, `autonomy-budget`, `harness-gc`, `pull-request-preparation`, `review-fix-loop`. **Evaluator analog:** `adversarial-reviewer` agent + `testing-validation` / eval harness.
5. **Plan consumers/producers:** `/plan-feature` → `implementation-planning`; `/implement-approved-plan` reads APPROVED plan; hooks + PR evidence read status; `close-workstream` marks COMPLETE.
6. **Approval hooks:** `plan-approval-check.sh` (critical, fail-closed); `pr-evidence-validation.sh` (soft).
7. **Install propagation:** copies `.cursor/{rules,skills,agents,hooks,commands}`; creates `.agent/{evidence,budgets,sessions,runs}`; does **not** copy `tests/` or control-only scripts unless added explicitly to install/update.
8. **Compatibility:** preserve Skill frontmatter contract (doctor); additive metadata only; plan Metadata block must remain hook-parseable.
9. **Orchestration state location:** control repo `orchestrator/` + generated artifacts under `.agent/capabilities/` (control) and optional `.agent/plans/<plan-id>/` during planning; product repos receive template + Skill updates via install.
10. **Representation:** JSON Schema + JSON artifacts for validation; YAML sidecars for human-authored capability metadata; Markdown for Captain-facing plan (approval surface).
11. **Min Capability schema:** id, version, kind, source, provenance, categories, tags, capabilities_provided, compatible_stacks, lifecycle_stage, security_sensitivity, agent_affinity (see Phase A).
12. **Min Task schema:** id, objective, acceptance_criteria, dependencies, required_capabilities, parallelizable, expected_artifacts.
13. **Min AgentManifest schema:** task_id, role, reference_profile, model, skills, tools, permissions, autonomy_budget, rationale, scoring_breakdown.
14. **Model provider:** static `ModelProfile` catalog in JSON; recommend class + optional slug list; no Cursor API integration in M1.
15. **Deterministic tests:** pure functions + golden fixtures; no LLM in CI (consistent with ADR-016).

### Reference agent profile migration (Captain guidance)

Preserve eight static agents as **known-good templates**:

```text
Existing static agents (.cursor/agents/)
        ↓
reference-profiles/*.json (extracted capabilities)
        ↓
AgentManifest.reference_profile
        ↓
Dynamic manifests per task
        ↓
Repeated evaluation (future)
        ↓
Possible persistent role promotion (future)
```

| Agent file | Reference profile ID | Primary capabilities (initial) |
|---|---|---|
| `repository-scout.md` | `repository-scout` | repo-discovery, stack-detection |
| `architecture-agent.md` | `architecture-agent` | system-design, contracts, rollback-planning |
| `implementation-agent.md` | `implementation-agent` | feature-implementation, convention-adherence |
| `test-engineer.md` | `test-engineer` | test-authoring, validation-evidence |
| `security-reviewer.md` | `security-reviewer` | security-review, threat-modeling |
| `accessibility-reviewer.md` | `accessibility-reviewer` | accessibility-review, inclusive-ui |
| `adversarial-reviewer.md` | `adversarial-reviewer` | defect-discovery, plan-compliance |
| `documentation-agent.md` | `documentation-agent` | project-memory-updates |

---

## Proposed Architecture

### Layered flow (M1)

```text
Vague objective + repo path
        ↓
repository-discovery (existing Skill) + PROJECT_CONTEXT
        ↓
orchestrator/intent — keyword/stack capability inference
        ↓
orchestrator/registry — load Skills + reference profiles
        ↓
orchestrator/planner — task graph (deterministic heuristics)
        ↓
orchestrator/matcher — rank Skills vs required capabilities
        ↓
orchestrator/assembler — AgentManifest proposals
        ↓
orchestrator/model_profiles — model class recommendation
        ↓
orchestrator/plan_writer — IMPLEMENTATION_PLAN sections
        ↓
First Mate presents plan → AWAITING APPROVAL → STOP
        ↓
(existing) /implement-approved-plan after Captain approval
```

### Module boundaries (new)

```text
orchestrator/
  schemas/                    # JSON Schema documents
  registry/
    loader.py                 # Skill + profile ingestion
    compiler.py               # build registry.json
    infer.py                  # fallback inference from description
  intent/
    infer_capabilities.py     # objective + repo signals → required capabilities
  planner/
    decompose.py              # objective → tasks + dependencies
    validate_graph.py         # cycle detection, missing deps
  matcher/
    score.py                  # deterministic explainable ranking
  assembler/
    manifest.py               # task → AgentManifest
  models/
    catalog.json              # ModelProfile definitions
    recommend.py
  plan_writer/
    render.py                 # Markdown sections for IMPLEMENTATION_PLAN
  providers/
    technology_intelligence/
      protocol.py             # Provider interface
      stub.py                 # returns [] until external engine exists

scripts/
  capability-plan.sh          # CLI wrapper for planning pipeline

.cursor/skills/
  capability-planning/        # NEW — First Mate procedure

.agent/   (control repo)
  capabilities/
    compiled/registry.json    # generated
  plans/<plan-id>/            # optional machine artifacts (task-graph.json, manifests.json)
```

### Knowledge architecture (future storage — M1 minimum)

| Category | M1 action |
|---|---|
| Knowledge | Unchanged (`PROJECT_CONTEXT.md`) |
| Decisions | Add ADR-017 on approval |
| Procedures | New `capability-planning` Skill |
| Performance | Schema stub only (`ExecutionRun`, `Experience`) |
| Artifacts | `.agent/plans/<plan-id>/` JSON + enhanced `IMPLEMENTATION_PLAN.md` |

### Technology Intelligence adapter (Phase H — interface only)

```python
# orchestrator/providers/technology_intelligence/protocol.py
class TechnologyIntelligenceProvider(Protocol):
    def discover_candidates(
        self, objective: str, context: dict
    ) -> list[CandidateCapability]: ...
```

- `CandidateCapability` carries `lifecycle_stage=DISCOVERED`, provenance, and **explicit not-approved** flag
- Stub provider returns empty list
- Plan section lists candidates separately from **approved** Skills
- No import from GitHub Star Categorization repo in M1

### Skill lifecycle (design-only in M1)

Document enum in schema; registry uses `AVAILABLE_SKILL` / `PROVEN_SKILL` for Compass Skills; candidates never auto-promote.

---

## Required Capabilities (for this milestone)

| Capability | Satisfied by |
|---|---|
| Schema design + validation | Phase A |
| Registry ingestion | Phase B |
| Capability inference + matching | Phase C |
| Task decomposition | Phase D |
| Agent manifest assembly | Phase E |
| Plan template integration | Phase F |
| Deterministic tests + fixtures | Phase G |
| Provider boundary stub | Phase H |
| Harness/docs/CI updates | Phases F–G |

---

## Reusable Capabilities Found (existing Compass assets)

| Asset | Reuse in M1 |
|---|---|
| `implementation-planning` | Extended output sections; still owns gate |
| `repository-discovery` | Input to intent inference |
| `worktree-orchestration` | Unchanged; referenced in Git Strategy section |
| `testing-validation` | Referenced in Testing Strategy |
| `autonomy-budget` | Manifest autonomy_budget fields |
| `harness-gc` | Validates new Skill/command drift after ship |
| Eight subagents | Reference profiles for manifests |
| `tests/evals/run.sh` pattern | Extend for planning sensors |
| `doctor.sh` Skill list | Extend with `capability-planning` + optional sidecar checks |

---

## Technology Intelligence Candidates

None wired in M1. Plan section will render:

> *No external candidates queried (Technology Intelligence provider: stub).*

Future: GitHub Star Categorization project connects via provider adapter only.

---

## Workstreams

Single sequential workstream (control repo). No parallel worktrees — shared files (`doctor.sh`, templates, tests).

---

## Phased Implementation

### Phase A — Architecture contracts

**Deliverables:**

- JSON Schemas (draft 2020-12):
  - `capability.schema.json`
  - `task.schema.json`
  - `agent-manifest.schema.json`
  - `model-profile.schema.json`
  - `candidate-capability.schema.json` (minimal)
  - `execution-run.schema.json` (stub for provenance fields)
- `orchestrator/` package init + `pyproject.toml` or requirements-dev pinning (stdlib-first; `jsonschema` if already acceptable — **prefer stdlib validation in M1 to avoid new runtime deps** unless Captain prefers `jsonschema`)
- ADR-017 draft: capability-aware planning foundation

**Schema minimums (illustrative):**

```yaml
# capability.yaml sidecar (optional per Skill)
id: react-engineering
version: "1.0.0"
kind: skill
source:
  type: compass-skill
  path: .cursor/skills/react-engineering/SKILL.md
lifecycle_stage: PROVEN_SKILL
categories: [frontend, ui]
tags: [react, typescript, accessibility]
capabilities_provided:
  - ui-component-implementation
  - client-state-management
compatible_stacks: [react, typescript, vite, nextjs]
security_sensitivity: low
agent_affinity: [implementation-agent]
maturity: proven
confidence: 0.9
```

### Phase B — Current Skill registry

**Deliverables:**

- `capability.yaml` for all 23 Skills (curated metadata)
- `reference-profiles/*.json` for 8 agents (extracted from existing `.md`)
- `orchestrator/registry/compiler.py` → `.agent/capabilities/compiled/registry.json`
- Inference fallback when sidecar missing (description keyword map — **should not trigger for M1 since we author all sidecars**)
- Duplicate `id` detection → hard fail at compile time

### Phase C — Capability resolver

**Deliverables:**

- `intent/infer_capabilities.py` — maps objective keywords + repo signals (from discovery JSON fixture or parsed PROJECT_CONTEXT) to required capability IDs
- `matcher/score.py` — weighted deterministic score:

  | Factor | Weight (initial) |
  |---|---|
  | capability overlap | 0.45 |
  | stack match | 0.20 |
  | lifecycle_stage (PROVEN > AVAILABLE) | 0.15 |
  | security task → security Skill bonus | 0.10 |
  | agent_affinity alignment | 0.10 |

- Every score includes human-readable `scoring_breakdown` array
- Unapproved candidates score 0 and cannot appear in `skills` list

### Phase D — Task graph planner

**Deliverables:**

- `planner/decompose.py` — rule-based decomposition (e.g., discovery → architecture → implementation → test → security → docs) adapted by domain detectors (frontend/backend/ml/security)
- `planner/validate_graph.py` — cycle detection, missing dependency IDs
- Output: `task-graph.json` adhering to Task schema

### Phase E — Agent manifest builder

**Deliverables:**

- `assembler/manifest.py` — one manifest per task
- Links `reference_profile` to static agent template
- Selects Skills from matcher top-N (default N=3 max per task)
- Assigns model class from `models/catalog.json`
- Sets autonomy budget defaults from plan template
- Output: `manifests.json`

### Phase F — Implementation Plan integration

**Deliverables:**

- Extend `templates/docs/IMPLEMENTATION_PLAN.md` with sections:
  - Required Capabilities
  - Reusable Capabilities Found
  - Technology Intelligence Candidates
  - Task Graph
  - Proposed Agent Configuration
  - Evaluation Strategy
  - Learning Plan
  - Approval Boundary (explicit stop)
- Update `.cursor/skills/implementation-planning/SKILL.md` to reference `capability-planning`
- New `.cursor/skills/capability-planning/SKILL.md`
- Update `.cursor/commands/plan-feature.md` to invoke capability pipeline
- `orchestrator/plan_writer/render.py` merges machine output into plan Markdown
- `scripts/capability-plan.sh` for local/CI invocation

**Hook compatibility:** no changes to `plan-approval-check.sh` logic; new sections are Markdown only.

### Phase G — Tests and evals

**Deliverables:**

- `tests/orchestrator/` — Python unit tests (pytest or unittest — match repo convention; **use unittest if no pytest yet**)
- Fixture objectives under `tests/fixtures/planning/`:

  | Fixture | Validates |
  |---|---|
  | `frontend-ui.json` | react + playwright Skills matched |
  | `backend-api.json` | node + prisma Skills matched |
  | `ml-pipeline.json` | python-ml matched |
  | `security-sensitive.json` | security-review + security-reviewer profile |
  | `multi-domain.json` | multiple tasks, parallelization flags |
  | `capability-gap.json` | explicit gap section, no silent fallback |

- Extend `tests/run.sh` — registry compile, schema validation smoke
- Extend `tests/evals/run.sh` — sensor: plan template contains required sections; stub provider isolation
- Extend `scripts/doctor.sh` — check `capability-planning` Skill, schemas present, registry compiles

### Phase H — Technology Intelligence provider boundary

**Deliverables:**

- Protocol + stub provider (Phase A/H merged)
- Document integration contract in `docs/integrations/technology-intelligence.md`
- Plan writer renders candidate table with **NOT APPROVED FOR EXECUTION** banner

---

## Task Graph (M1 implementation meta-plan)

| ID | Objective | Depends on | Parallelizable |
|---|---|---|---|
| T-A | Schemas + package skeleton | — | — |
| T-B | Skill sidecars + profile extraction + registry compiler | T-A | — |
| T-C | Intent inference + matcher | T-B | — |
| T-D | Task planner + graph validation | T-A | — |
| T-E | Manifest assembler + model catalog | T-C, T-D | — |
| T-F | Plan writer + template/command/Skill updates | T-E | — |
| T-G | Tests, evals, doctor, install/update | T-F | — |
| T-H | Provider stub + integration doc | T-A | T-G |

---

## Proposed Agent Configuration (for this control-repo work)

| Task | Reference profile | Skills | Model class | Rationale |
|---|---|---|---|---|
| T-A–E | `architecture-agent` | `implementation-planning` | reasoning-strong | Schema/module design |
| T-F | `implementation-agent` | `capability-planning`, `implementation-planning` | coding-strong | Template + Skill integration |
| T-G | `test-engineer` | `testing-validation` | coding-strong | Deterministic tests |
| T-H | `architecture-agent` | `implementation-planning` | reasoning-strong | Provider boundary doc |
| Final review | `adversarial-reviewer` | — | inherit | Plan + test gap review |

---

## Files Expected to Change

### New files (representative)

```text
orchestrator/**                          # Python package
scripts/capability-plan.sh
.cursor/skills/capability-planning/SKILL.md
.cursor/skills/*/capability.yaml         # 23 sidecars
orchestrator/reference-profiles/*.json   # 8 profiles
orchestrator/schemas/*.schema.json
orchestrator/model_profiles/catalog.json
tests/orchestrator/test_*.py
tests/fixtures/planning/*.json
docs/integrations/technology-intelligence.md
docs/adr/ADR-017-capability-aware-planning.md  # or DECISIONS.md entry
.agent/capabilities/compiled/.gitkeep
```

### Modified files

```text
IMPLEMENTATION_PLAN.md                   # this plan → later COMPLETE on ship
templates/docs/IMPLEMENTATION_PLAN.md
.cursor/skills/implementation-planning/SKILL.md
.cursor/commands/plan-feature.md
scripts/doctor.sh
scripts/install.sh                        # if orchestrator assets must propagate
scripts/update.sh
tests/run.sh
tests/evals/run.sh
PROJECT_CONTEXT.md                        # repository map + orchestrator note
DECISIONS.md                              # ADR-017
PROGRESS.md
CHANGELOG.md
TESTING.md
README.md                                 # v1.5.0 feature bullet
VERSION                                   # on release
```

### Explicitly not modified in M1

- `.cursor/hooks/plan-approval-check.sh` (behavior)
- Product example app code under `examples/` (unless test fixtures only)
- Existing agent `.md` bodies (profiles extracted, not rewritten)

---

## Parallelization Plan

Implementation is **sequential** (single developer/agent, shared harness files).

Future product tasks may use parallel manifests when task graph marks `parallelizable: true` and file boundaries are disjoint (existing `worktree-orchestration` rules apply **after** approval).

---

## Testing Strategy

Classify as **control-repo infrastructure** per evidence matrix.

| Layer | M1 action |
|---|---|
| Static analysis | Python syntax check; optional ruff if already in repo |
| Unit tests | orchestrator modules + fixtures (6 scenarios) |
| Integration | `capability-plan.sh` end-to-end on fixtures → plan sections |
| Schema tests | malformed capability, duplicate ids, cyclic deps |
| Harness | extend `tests/run.sh`, `tests/evals/run.sh` |
| Security review | ensure candidate capabilities cannot grant execution; no secret paths in registry |
| Approval gate | eval proves DRAFT still denies product edits |
| Install smoke | temp repo install still passes doctor |
| Production build | N/A (no app deploy) |
| Rollback | tag restore + revert VERSION |

Evidence path: `.agent/evidence/m1-capability-aware-planning/`

---

## Security Review

- Candidate capabilities from future providers must remain **read-only suggestions**
- Agent manifests include least-privilege language; no broad tool grants by default
- Registry compiler rejects path traversal in `source.path`
- Sidecar YAML must not embed secrets
- No automatic code fetch from external repos

---

## Accessibility Review

Not applicable (no UI). Documentation must remain plain-language and structured.

---

## Migration Plan

**Backwards compatibility:**

1. Skills without `capability.yaml` continue to work; inference fallback logs warning in compile output
2. Existing product repos: `update.sh` adds new Skill + template sections; old plans remain valid
3. Hooks unchanged — plans without new sections still gate correctly
4. Static agents remain in `.cursor/agents/` unchanged

**Migration steps for product repos:**

1. Update Compass to v1.5.0
2. Run doctor
3. Next `/plan-feature` uses capability planning automatically

---

## Deployment Plan

- Merge to `main` via PR after validation
- Tag `v1.5.0`
- Sandbox repo exercise: run `/plan-feature` on a sample objective; verify enhanced plan + approval gate

---

## Rollback Plan

1. Restore from tag `rollback/pre-m1-capability-aware-planning`
2. Revert VERSION to 1.4.0
3. Product repos: forward-only update policy means stay on 1.4.0 until ready to retry

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Over-engineering orchestrator | Delay, maintenance | M1 vertical slice only; stdlib-first |
| Skill metadata drift | Wrong routing | doctor compile + harness-gc Skill |
| Plan template breaks hooks | Approval bypass | hook evals unchanged; template Metadata first |
| False capability match | Bad plans | explainable scores + gap fixture |
| Scope creep into execution | Safety regression | explicit non-goals; separate milestone |
| Install size/complexity | Product friction | control-only Python; optional script in product |

---

## Evaluation Strategy

M1 succeeds when:

1. Same fixture objective → identical task graph + top Skill picks (deterministic)
2. `capability-gap` fixture → plan contains **Capability Gap** section with recommended next steps
3. Captain can read rationale for every manifest without opening JSON
4. `./tests/run.sh` and `./tests/evals/run.sh` green in CI

Post-ship: manual sandbox checklist row for capability-aware `/plan-feature`.

---

## Learning Plan

After execution (future milestone), retain under `.agent/plans/<plan-id>/`:

- `task-graph.json`
- `manifests.json`
- `registry.snapshot.json` (registry hash)
- Link to Git issue/branch/PR when implementation occurs

M1 defines schemas and directories; population happens in Milestone 2 (execution telemetry).

---

## Autonomy Budget

After approval, create `.agent/budgets/m1-capability-aware-planning.md`.

- Maximum iterations: 25
- Maximum failed validation cycles: 5
- Maximum estimated cost: Captain-defined
- Maximum elapsed time: 5 working days
- Budget ledger path: `.agent/budgets/m1-capability-aware-planning.md`
- On limit: `.agent/evidence/m1-capability-aware-planning/BUDGET_STOP_REPORT.md`

---

## Definition of Done

- All Acceptance Criteria checked
- `./scripts/doctor.sh` passes
- `./tests/run.sh` passes (target: existing 85+ tests + new orchestrator tests)
- `./tests/evals/run.sh` passes
- Security review complete (control-repo checklist)
- ADR-017 accepted
- PROGRESS.md, CHANGELOG.md, TESTING.md updated
- PR prepared with evidence under `.agent/evidence/m1-capability-aware-planning/`
- No implementation on protected branches

---

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Approval means:

1. Record approval below
2. Set Status to **APPROVED**
3. Create GitHub issue
4. Create rollback tag
5. Create feature branch `feature/<issue>-m1-capability-aware-planning`
6. Begin Phase A

Until then, only planning documents and discovery artifacts may change.

---

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-19
- **Approved revision:** M1 capability-aware planning foundation; sidecar metadata per ADR-017
- **Issue:** [#35](https://github.com/loganware05/captains-compass-cursor/issues/35)
- **Branch:** `feature/35-m1-capability-aware-planning`
- **Rollback:** `rollback/pre-m1-capability-aware-planning` @ `5929f10`

**In progress:** Phase H — Technology Intelligence provider doc finalization.

**Phase G complete (2026-08-19):** integration golden tests (6 fixtures), path-traversal registry guard test, install propagation (`.agent/capabilities/compiled`, `.agent/plans`, capability-planning sidecar), doctor fixture/schema checks, eval stub-TI isolation + golden determinism — **103/103 tests, 21/21 evals**.

**Phase F complete (2026-08-19):** plan writer, `capability-plan.sh`, `capability-planning` Skill, enhanced plan template, `/plan-feature` integration, technology-intelligence doc.

**Phase E complete (2026-08-19):** per-task agent manifests with reference profiles, Skill selection (top 3), model class recommendations, autonomy budget defaults, `build-agent-manifests.sh`.

**Phase D complete (2026-08-19):** rule-based task decomposition, cycle/missing-dependency validation, topological ordering, `plan-task-graph.sh`, planner tests.

**Phase C complete (2026-08-19):** intent inference, deterministic Skill matcher with explainable scoring, resolver API, six planning fixtures, `capability-resolve.sh` CLI.

**Phase B complete (2026-08-19):** 23 `capability.yaml` sidecars, 8 reference agent profiles, registry compiler, stdlib YAML loader, inference fallback, doctor/CI compile step.

**Phase A complete (2026-08-19):** JSON Schemas, `orchestrator/` package skeleton, stdlib validator, model catalog, Technology Intelligence stub provider, orchestrator unit tests, doctor/test integration.
