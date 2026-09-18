# Implementation Plan — M40 / Filesystem-Gated Context & Dependency Architecture

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `m40-filesystem-gated-context` |
| Supersedes | — (builds on M17 context selection, M27–M33 Code Reviewer, M9/M23 skill lifecycle) |
| Product | **NorthStar** |
| Baseline | **v1.40.1** @ `125d53e` (M38 + M39 merged; prior plan archived at `docs/plans/AGENTIC_SECURITY_REVIEW_PHASE_B.md`) |
| Prepared | 2026-09-18 |
| Milestone spec | Captain-provided "Filesystem-Gated Context & Dependency Architecture" (2026-09-18, full text received in two parts) |
| Control repo | `loganware05/captains-compass-cursor` |
| Validation proving ground | `loganware05/captain-compass-sandbox` (React/TS Vite) |
| Proposed release | **v1.41.0** (tentative) |
| Rollback checkpoint | SHA `125d53e`; tag `rollback/pre-m40-filesystem-gated-context` to be created at approval |
| Branch | `cursor/m40-filesystem-gated-context-ea39` |
| Issue | Local placeholder per ADR-004 — Captain to file GitHub issue (gh is read-only for the agent) |
| Captain | Logan Ware |

> Path note: the milestone spec references `.agent/IMPLEMENTATION_PLAN.md`. Repo
> convention and the fail-closed plan-approval hook gate on **root**
> `IMPLEMENTATION_PLAN.md`, so this file is the authoritative plan. Machine
> planning artifacts (`resolve.json`, `task-graph.json`, `manifests.json`) live
> under `.agent/plans/m40-filesystem-gated-context/` per the spec's Planning Phase.

## Request

Upgrade NorthStar's Python orchestrator, capability planning engine, and code
reviewer with operating-system filesystem patterns:

1. **Task 1 — Hierarchical Context Router & Inode Metadata Store**: sequential
   directory-style context route walking (`.agent/context/<domain>/<module>/`)
   instead of monolithic context dumps; an inode-style metadata store
   (`.agent/inodes/`) indexing structural metadata (exported TS interfaces,
   function signatures, I/O types, declared complexities) decoupled from raw
   source; subagents load only relevant inode pointers for their module scope.
2. **Task 2 — Hard/Symlinked Dependency Graph & Boundary Review Gate**:
   `task-graph.json` dependencies gain explicit hard-linked contract definitions
   and symlinked module path references; `northstar review` gains a
   cross-boundary verification gate that validates interface types and
   algorithmic complexity (declared \(O(N)\) vs \(O(N^2)\)) against metadata
   inodes before a plan/review passes.
3. **Task 3 — Content-Addressed Skill Inodes & Subagent `pwd` Isolation**:
   Technology Intelligence skill registry indexes proven skills by
   content-addressed hash IDs (`.cursor/skills/inodes/`); `agent-manifest`
   assembly gives each spawned specialist an isolated working context (`pwd`)
   with restricted scope, preventing context state pollution during parallel
   subagent execution.

## Problem Statement (evidence-based)

- **Flat memory grows monotonically.** The always-on startup rules read
  `PROJECT_CONTEXT.md`, `DECISIONS.md` (~1000 lines, 56 ADRs), `PROGRESS.md`,
  `TESTING.md` in full every session. Context cost scales with project history,
  not with the task — the "lost in the middle" risk the spec names.
- **Retrieval is flat.** `orchestrator/knowledge/` (TF-IDF/dense, ADR-022/027)
  and `orchestrator/planning/context_selection.py` (M17) return top-N slices by
  objective-string similarity; nothing scopes context by module boundary.
- **Task-graph dependencies are ordering strings only.**
  `orchestrator/schemas/task.schema.json` defines `dependencies` as
  `array<string>`; `orchestrator/planner/decompose.py` emits phase edges
  (`task-architecture` → `task-impl-*`). No contract or module-path semantics.
- **Review never crosses boundaries.** `orchestrator/review/investigate.py`
  builds context packs from changed files + same-directory siblings (≤12
  neighbors, 16 KB/file); `verify.py` is a confidence/severity ranker. No call
  site is checked against a callee signature. The continuation roadmap already
  lists "Verification depth" as the Code Reviewer's primary gap.
- **Skill identity is slug-keyed and mutable.** `orchestrator/registry/compiler.py`
  hardcodes `SKILL_SLUGS`; PROVEN_SKILL reputation (ADR-025/050) attaches to the
  slug, so editing a proven Skill silently inherits its reputation.
- **No per-subagent working context.** `orchestrator/assembler/manifest.py`
  selects role/skills/model per task but does not scope context; parallel
  specialists share the whole-repo view.

## Proposed Architecture

### Task 1 — `orchestrator/context/` (new package)

1. **`walker.py` — directory-style route resolver.** Resolves context routes
   (`.agent/context/<domain>/<module>/`) segment-by-segment: each directory
   level carries a small generated `node.json` (summary + child index +
   inode refs); the walker loads only the nodes on the walked path and returns
   ordered context pointers. Never dumps the tree.
2. **`inodes.py` — inode metadata store.** `.agent/inodes/<sha256>.json` per
   indexed source file: source path, content hash (staleness), exported symbols
   (TS interfaces, function signatures, I/O types), declared complexity,
   byte size. Raw source is never copied — inodes are pointers + metadata.
3. **`extract.py` — hermetic structural extractors.** Python via stdlib `ast`;
   TypeScript/TSX via a parser-lite extractor validated against fixtures
   (control CI stays stdlib-only — no node dependency). Declared complexity is
   read from an explicit annotation convention (e.g. `@complexity O(N)` in
   docstring/JSDoc); it is **declared metadata, not inferred**.
4. **Derived hierarchy.** The `.agent/context/` tree is *derived* from repo
   directory structure + `domains_detected` (intent inference), not
   hand-authored — avoids taxonomy drift (harness-gc territory).
5. **Schemas + CLI + doctor.** New `context-inode.schema.json` and
   `context-route.schema.json`; explicit CLI `scripts/build-context-inodes.sh`
   and `northstar context build|walk`; `doctor.sh` gains a staleness check
   (inode content hash vs source hash). Rebuild is explicit-only, consistent
   with the vector-index rebuild pattern (ADR-022).
6. **Context window optimization.** Plan writer and manifest assembly reference
   inode IDs + walked routes instead of inlining blobs; an eval under
   `tests/evals/` records prompt-payload bytes before/after on a fixed fixture
   so the savings are measured, not asserted.

### Task 2 — `orchestrator/dependency_graph.py` + review boundary gate

1. **Typed links in planning (backward compatible).** `task.schema.json`
   dependencies accept either the legacy string form (ordering edge) or an
   object: `{ "target": "<task-id>", "link": "hard" | "symlink", "contract":
   "<inode-id or interface name>", "paths": ["<module path>"] }`.
   - **hard link** — version-locked contract coupling: both sides must change
     together; review must verify both ends against the same contract inode.
   - **symlink** — loose module path reference through indirection; review
     checks the reference resolves and types conform.
   `decompose.py` emits typed links; `validate_graph.py` accepts both forms
   (existing fixtures/graphs keep passing).
2. **`dependency_graph.py`.** Builds the module-level link graph from inode
   import edges (TS `import … from`, Python `import`): edges typed `hard` when
   both modules share a contract inode (interface/signature), `symlink` for
   path-only references.
3. **Boundary precision gate.** New `orchestrator/review/boundary.py` candidate
   emitter following the M28 `specialists.py` pattern, wired into
   `run_code_review` (`--boundary-check`; default on when an inode store is
   present, explicit skip note when absent):
   - For each changed file, enumerate cross-boundary calls (imports from a
     different context domain/module).
   - Validate call sites against callee inode signatures (exported symbol
     exists; arity/type-name conformance where extractable).
   - Complexity conformance: flag call sites whose usage pattern contradicts
     the callee's declared complexity (e.g. nested-loop invocation per element
     of an imported collection against an \(O(N)\) declaration ⇒ effective
     \(O(N^2)\)). Scoped to declared metadata + heuristic mismatch — **no full
     static complexity inference**.
   - Findings flow through the existing `verify_findings` ranking; output
     remains evidence-only (M27 lock), hermetic, no model calls.
4. **Fixtures.** `tests/fixtures/code-review/boundary/` — fixture inode store +
   diffs with seeded cross-boundary type violations and complexity mismatches,
   plus clean controls.

### Task 3 — Skill inodes + manifest `pwd`

1. **Content-addressed Skill inodes.** New `orchestrator/registry/inodes.py`;
   index at `.cursor/skills/inodes/<sha256>.json` (spec path) containing:
   content hash over `SKILL.md` + `capability.yaml`, slug, lifecycle stage,
   live path pointer, created-at. `registry/compiler.py` computes and embeds
   `content_hash` per entry; the compiled registry references inode IDs.
2. **Reputation integrity.** Experience/proficiency records may pin the
   `skill_inode` hash they were earned against. When Skill content changes, the
   hash changes → new inode; lifecycle-stage carry-over to the new inode
   requires an explicit Captain-approved proposal (consistent with ADR-025 and
   ADR-050: no silent reputation mutation). Slugs remain the human-facing
   identity; hashes are machine keys.
3. **`pwd` sandboxing in manifest assembly.** `orchestrator/assembler/manifest.py`
   gains a `working_context` block per manifest: `context_root` (scoped
   `.agent/context/<domain>/<module>/` route), `inode_refs` (only in-scope
   module inodes + shared contract inodes), `scope_allow` / `scope_deny` path
   lists. `agent-manifest.schema.json` updated accordingly. Parallel manifests
   for disjoint modules must share no inode refs except declared hard-link
   contracts — that is the pollution-prevention invariant, checked by a
   deterministic eval.
   - **Honest scope note:** `pwd` isolation is advisory-by-construction at the
     manifest layer (the manifest declares the scope; agents are instructed to
     stay within it). Hard runtime enforcement is a Cursor-platform concern and
     is out of scope.

## Mandatory Execution & Safety Lifecycle (spec mapping)

1. **Planning Phase — complete.** `resolve.json`, `task-graph.json`,
   `manifests.json` constructed under `.agent/plans/m40-filesystem-gated-context/`
   via `scripts/capability-plan.sh`; this plan authored at root (see path note).
2. **Captain Approval Gate — THIS DOCUMENT.** No implementation file under
   `orchestrator/` will be modified until this plan is APPROVED, committed, and
   carries a real Approval Record (fail-closed hook enforced).
3. **Sandbox Validation (post-approval).** `scripts/update.sh` into
   `captain-compass-sandbox` on a sandbox feature branch; build inodes over
   sandbox `src/`; run `npm run lint`, `npm run test`, `npm run build`; open a
   sandbox PR exercising a cross-boundary change.
4. **Evidence & Review (post-approval).** Run `northstar review` with the
   boundary gate against the sandbox PR and fixture corpus. "100% boundary
   precision" is operationalized as: on the fixture + sandbox validation corpora,
   precision = TP/(TP+FP) = 1.0 against inode ground truth, and all seeded
   violations detected — measured and logged, not asserted. Reports/diffs under
   `.agent/evidence/m40-filesystem-gated-context/`.

## Acceptance Criteria

1. Plan-gated ✅ (this doc AWAITING APPROVAL → Captain approves)
2. Inode store + walker: hermetic, deterministic build (same source ⇒ same
   hashes) over control repo + fixtures; doctor staleness check fails closed on
   stale inodes with a rebuild hint
3. Route walking: a module-scoped manifest references only its route's inodes;
   `tests/evals/` records prompt-payload byte reduction vs the monolithic
   baseline on a fixed fixture
4. Typed links: `task.schema.json` accepts string and object dependencies;
   planner emits hard/symlink links; existing graphs/fixtures unchanged and green
5. Boundary gate: fixture corpus yields precision 1.0 (no false positives on
   clean controls) and detects all seeded cross-boundary type/complexity
   violations; integrated into `northstar review` evidence-only path; hermetic,
   no model, stdlib-only in CI
6. Skill inodes: registry compile embeds content hashes; editing a SKILL.md
   yields a new inode; stage carry-over requires Captain-approved proposal;
   `.cursor/skills/inodes/` index built for all 41 Skills
7. `pwd` isolation: manifests carry `working_context` with scope allow/deny;
   eval proves disjoint-module parallel manifests share only declared contract
   inodes
8. Sandbox: `npm run lint`, `npm run test`, `npm run build` green on the sandbox
   branch; boundary review report + diffs logged under `.agent/evidence/`
9. `./scripts/doctor.sh`, `./tests/run.sh`, `./tests/evals/run.sh` all green;
   hermetic CI preserved (no node, no network, no model on default path)
10. Documentation: ADR-057, PROJECT_CONTEXT / DECISIONS / PROGRESS / TESTING /
    CHANGELOG updates; Skill updates (`capability-planning`, `code-reviewer`,
    `skill-lifecycle`) + one new Skill `context-inodes`

## Non-Goals

- True static complexity inference (declared metadata + heuristics only)
- Runtime enforcement of `pwd` isolation inside the Cursor platform
- Hosted vector DB / live embedding provider changes
- Any auto-apply, auto-merge, or live Skill install — all Captain gates preserved
- Renaming the `code-reviewer` Skill slug or changing M27–M33 review locks
- Sandbox product features beyond what validation requires
- Migrating historical Experience/proficiency records to inode pins (additive
  going forward)

## Workstreams

| WS | Scope | Depends on |
|---|---|---|
| WS1 | Schemas + inode store + extractors + build CLI (Task 1.2) | — |
| WS2 | Context walker + route resolution + plan-writer context-route section (Task 1.1, 1.3) | WS1 |
| WS3 | Typed task-graph links + `dependency_graph.py` (Task 2.1) | WS1 |
| WS4 | Boundary review gate + fixtures + precision measurement (Task 2.2) | WS1, WS3 |
| WS5 | Skill inodes + registry compiler integration (Task 3.1) | — |
| WS6 | Manifest `working_context` / `pwd` scoping + isolation eval (Task 3.2) | WS1, WS2 |
| WS7 | Sandbox validation + evidence + docs + ADR-057 + release prep | WS1–WS6 |

Parallelization: WS1+WS5 land first; WS2/WS3 then parallel; WS4/WS6 parallel;
WS7 sequential. Worktrees per rule 02 if parallelized.

## Files Expected to Change

- New: `orchestrator/context/{__init__,walker,inodes,extract}.py`,
  `orchestrator/dependency_graph.py`, `orchestrator/review/boundary.py`,
  `orchestrator/registry/inodes.py`,
  `orchestrator/schemas/{context-inode,context-route}.schema.json`,
  `scripts/{build-context-inodes.sh}` + `scripts/northstar` wiring,
  `tests/orchestrator/test_m40_*.py`, `tests/fixtures/context/**`,
  `tests/fixtures/code-review/boundary/**`, `.cursor/skills/context-inodes/`
- Modified: `orchestrator/planner/decompose.py`,
  `orchestrator/planner/validate_graph.py`, `orchestrator/schemas/task.schema.json`,
  `orchestrator/schemas/agent-manifest.schema.json`,
  `orchestrator/assembler/manifest.py`, `orchestrator/registry/compiler.py`,
  `orchestrator/review/pipeline.py`, `orchestrator/plan_writer/render.py`,
  `scripts/doctor.sh`, `scripts/run-code-review.sh`, `tests/evals/run.sh`,
  `.cursor/skills/{capability-planning,code-reviewer,skill-lifecycle}/`,
  memory docs + CHANGELOG + VERSION (v1.41.0)

## Testing Strategy

Evidence matrix rows: orchestrator/control change → unit tests
(`tests/orchestrator/test_m40_*.py`), deterministic evals (`tests/evals/`:
inode build determinism, route-walk scoping, boundary precision = 1.0 on
fixtures, manifest isolation invariant), doctor checks, hermetic CI. Sandbox
product change → `npm run lint` / `npm run test` / `npm run build` + review
evidence. All artifacts under `.agent/evidence/m40-filesystem-gated-context/`.

## Security Notes

- Inodes contain structural metadata (names, signatures, hashes) — never file
  contents; reuse `redact_secrets` on any embedded snippet.
- SHA-256 content addressing; no secrets, tokens, or network on the default path.
- All existing fail-closed locks preserved (plan gate, protected branch,
  secrets); new gates are additive only.

## Review Domains

- python, security, tests

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Stale inodes → false confidence in review gate | Content-hash staleness detection; doctor check; explicit rebuild CLI; boundary gate skips with explicit note when store is stale/absent |
| Complexity analysis overclaim | Scoped to declared annotations + heuristic mismatch; plan and docs state this explicitly |
| Context taxonomy drift | Hierarchy derived from repo structure + inferred domains, never hand-maintained; harness-gc can audit |
| Unmeasured context savings | Deterministic eval records payload bytes before/after on fixed fixtures |
| Schema churn breaking existing graphs | Backward-compatible union type for dependencies; existing fixtures must pass unchanged |
| Spec arrived truncated (Task 3) | Full text confirmed with Captain 2026-09-18; this plan covers the complete spec |

## Autonomy Budget

Ledger: `.agent/budgets/m40-filesystem-gated-context.md` (created with this
plan; updated each cycle per Skill `autonomy-budget`).

- Maximum iterations: 40 implementation/validation cycles
- Maximum failed validation cycles: 6 consecutive → stop with Budget Stop Report
- Scope stop: any change outside "Files Expected to Change" → return to gate
- Hard stop: never weaken fail-closed hooks, tests, or existing review locks
- On limit: write `.agent/evidence/m40-filesystem-gated-context/BUDGET_STOP_REPORT.md` and stop

## Rollback Plan

- Checkpoint: SHA `125d53e`; tag `rollback/pre-m40-filesystem-gated-context` at approval.
- All new modules are additive; revert = delete new files + revert modified
  planner/registry/manifest/review files to tag.
- Schema changes are backward compatible; existing task graphs and review
  fixtures pass with or without the new fields.
- Boundary gate and context walker skip cleanly when `.agent/inodes/` is absent,
  so a partial rollback cannot wedge `northstar review` or planning.
- Sandbox branch is disposable; sandbox `main` untouched until evidence is green.

## Definition of Done

Acceptance criteria 1–10 satisfied; evidence logged; ADR-057 recorded; memory
docs updated; PR merged (or explicit Captain stop). Status moves to COMPLETE
only after merge.

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**
Machine-generated capability matches and agent manifests under
`.agent/plans/m40-filesystem-gated-context/` are proposals only.

## Approval Record

<!-- After Captain approval, record who approved, when, and the plan revision.
     Promoting Status via Write/StrReplace requires COMPASS_CAPTAIN_APPROVE=1
     (see .cursor/hooks/README.md). Commit the plan before product-source edits. -->

- Approved by: _pending_
- Approval date: _pending_
- Approved revision: _pending_

---

## Generated Capability Sections (Planning Phase output)

Source: `scripts/capability-plan.sh --plan-id m40-filesystem-gated-context`
(artifacts: `.agent/plans/m40-filesystem-gated-context/{resolve,task-graph,manifests}.json`).

### Required Capabilities

Inferred from the objective and repository context.

- react-component-development, typescript-ui, component-testing,
  keyboard-navigation-review, node-api-development, auth-boundary-enforcement,
  request-validation, server-integration-tests, python-service-development,
  ml-training, ml-evaluation, experiment-reproducibility,
  implementation-plan-authoring, approval-gate-enforcement, scope-definition,
  rollback-planning, unit-test-execution, integration-test-execution,
  definition-of-done-validation, validation-evidence-capture

**Domains detected:** react, node, python, plan, test

### Reusable Capabilities Found (top 5, deterministic matcher)

| Skill | Score |
|---|---:|
| `implementation-planning` | 0.39 |
| `node-engineering` | 0.39 |
| `python-ml` | 0.39 |
| `testing-validation` | 0.39 |
| `react-engineering` | 0.3675 |

**Capability gaps:** none detected.

### Technology Intelligence Candidates

> **NOT APPROVED FOR EXECUTION** — discovery signals only. Provider: `stub`
> (hermetic default; none queried).

### Task Graph (generated draft)

Execution order: task-discovery → task-architecture → task-impl-frontend →
task-impl-backend → task-impl-ml → task-validation → task-security-review →
task-documentation (8 tasks; see
`.agent/plans/m40-filesystem-gated-context/task-graph.json`). WS1–WS7 above
refine this draft; typed hard/symlink links land in WS3.

### Proposed Agent Configuration

8 task manifests generated (`.agent/plans/m40-filesystem-gated-context/manifests.json`);
WS6 adds the `working_context` / `pwd` block to this assembly path.
