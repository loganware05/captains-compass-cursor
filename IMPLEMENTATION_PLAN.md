# Implementation Plan — Bend Policy-Lifecycle Proof Spike

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `bend-policy-proof-spike` |
| Issue | #278 (https://github.com/loganware05/captains-compass-cursor/issues/278) |
| Baseline | `origin/main` @ `ef0ca3203ff1e30e5455aae0dba944125bad250b` (v1.87.0) |
| Branch | `feature/278-bend-policy-proof-spike` from `main` (worktree `../captains-compass-cursor-bend-spike`) |
| Rollback | `rollback/pre-bend-policy-proof-spike` @ `ef0ca32` |
| Proposed release | minor, **opt-in / experimental**; no authority-lock change; version assigned at release |
| Created | 2026-11-18 |
| Approved by | Logan Ware (Captain) — chat "Approve" |
| Approval date | 2026-11-18 |
| Approved revision | Q1=replace active plan file; Q2=policy lifecycle only; Q3=isolated project-local toolchain; Q4=default budget; Q5=`LAWS.bend` Captain-reviewed (Captain accepted recommended defaults) |
| Bend pin | Release `v2.0.40` (tag `624dd9f`), sha256-verified prebuilt + Lean `v4.34.0` — refined at Wave 0 from `bendlang/bend@9c586f0`; see `.agent/evidence/bend-policy-proof-spike/wave0-provenance.md` (Apache-2.0) |

Budget: `.agent/budgets/bend-policy-proof-spike.md`  
Durable copy: `docs/plans/BEND_POLICY_PROOF_SPIKE.md`  
Source analysis: Captain thread 62fcd31d-9f2e-448b-943b-14022585e272 (Bend repo assessment, 2026-11-18).

**Supersedes as active gate:** `post-merge-wave-continue` (now COMPLETE on `main`). Its text remains in `docs/plans/POST_MERGE_WAVE_CONTINUE.md`.

## Request

Using the previous Bend assessment, plan a **small, bounded experiment** to learn whether Bend 2 formal proofs give NorthStar stronger evidence for a safety-critical decision core, before any wider adoption.

## Findings carried from the Bend assessment

- Bend 2 = dependent types + proofs + CPU/GPU compile. Strongest fit for NorthStar is **verification**, not performance.
- Proofs cover a *Bend model*, not the existing Python/Bash. A conformance link between model and implementation is required for the proof to mean anything operationally.
- Documented limits: no built-in JSON/HTTP, slow strings, no proof tactics; compiler ~99% AI-written and unaudited; `--verdict` kernel is proven but parser/translation into it is not; backends can diverge from semantics.
- Install route is `curl | sh`; native build needs clang 14+. Neither `bend` nor `lean` is installed on this machine today.
- Bend CI pattern worth borrowing independently: load gate files from `main`, not the PR tree.

## Current implementation (investigated)

| Component | Location | Relevance |
|---|---|---|
| Lifecycle states + transitions | `orchestrator/behavior/policy/states.py` | 7 states, `TRANSITIONS` table, `CAPTAIN_REQUIRED = {approved, active, proven, retired}`, `can_transition()`. Pure, small. **Spike target.** |
| Promotion gates | `orchestrator/behavior/policy/gates.py` | `require_captain_approved`, prompt-eval pass, shadow-present, proven-evidence threshold. Evidence gates read the filesystem (out of proof scope; modeled as boolean preconditions). |
| Promotion orchestration | `orchestrator/behavior/policy/promote.py` | Order: legality → Captain gate → per-state evidence gates. Spike will mirror the decision order, not rewrite it. |
| Task graph validator | `orchestrator/planner/validate_graph.py` | Candidate for a **later** spike (cycles, missing deps, topological order). Out of scope here. |
| Plan-approval hook | `.cursor/hooks/plan-approval-check.sh` | Shell + embedded Python, regex based. Not modeled in this spike. |

## Scope

### In scope

1. **Pinned, isolated Bend toolchain** (sandbox only; no global install, no `curl | sh` on the Captain's machine without review).
2. **Bend model** of the promotion *decision core*: pure function `decide(from_state, to_state, captain_approved, preconditions) → accept | reject(reason)`.
3. **Captain-owned laws file** (`LAWS.bend`) and agent-written proofs, separated per Bend convention.
4. **Proved properties** (initial set):
   - **P1 legality:** `accept` ⇒ edge exists in the transition table.
   - **P2 Captain gate:** `accept` ∧ `to ∈ CAPTAIN_REQUIRED` ⇒ `captain_approved = true`.
   - **P3 terminal:** nothing is accepted out of `retired`.
   - **P4 monotone/acyclic (per step — see Amendment A1):** every accepted transition strictly increases stage rank, for all inputs.
   - **P5 shadow-before-approval (per step — see Amendment A1):** every accepted entry into `approved` comes from `shadowed`, for all inputs.
   - **P6 no authority grant:** the model has no output that sets execution authority (readiness-style, mirrors `approved_for_execution=False` / `authority_mutation=False` invariants).
5. **Conformance bridge** (Python ↔ model), without rewriting production code:
   - Export `LIFECYCLE_STATES`, `TRANSITIONS`, `CAPTAIN_REQUIRED` from `states.py` to canonical JSON.
   - Differential test: exhaustively enumerate all `7 × 7 × {approved: T/F} × 16 evidence combinations` (1568) inputs (extended from `7 × 7 × 2` — Amendment A2); compare Python `can_transition` + `require_captain_approved` outcomes to Bend model outcomes.
   - Drift test: fail if the Python tables change without regenerating/re-proving the model.
6. **Mutation checks** (negative controls): deliberately inject illegal edges, drop a state from `CAPTAIN_REQUIRED`, make `retired` non-terminal; proofs/conformance must **fail**. Recorded as evidence that the harness can actually reject.
7. **Evidence record:** compiler SHA, `LAWS.bend` hash, model hash, command, exit status, `--verdict` result, timings → `.agent/evidence/bend-policy-proof-spike/`.
8. **Opt-in CLI/CI surface:** `COMPASS_BEND_PROOF_ENABLED=1 ./scripts/northstar formal check policy-lifecycle`. Skips (not fails) when Bend is absent, so existing doctor/CI stay green by default.
9. **Spike report with go / no-go** metrics (see Decision Gate).

### Out of scope / non-goals

- Replacing or generating production Python/Bash from Bend.
- GPU/CPU acceleration, benchmarking performance, or any runtime dependency on Bend.
- Modeling hooks, JSON parsing, filesystem state, or evidence-gate internals.
- Task-graph / planner proofs (candidate follow-up only if the Decision Gate passes).
- Changing promotion behavior, `states.py` semantics, authority locks, or auto-approval anything.
- Making Bend a required dependency of install/update/doctor.

## Waves

### Wave 0 — Toolchain provenance & feasibility (stop-early gate)

- Run Skill `dependency-supply-chain` on Bend: license, maintainers, release/commit pinning, install script contents, transitive requirements (clang, Node, Lean).
- Build/install from the **pinned commit** into an isolated prefix (e.g. `.agent/tools/bend/`, git-ignored) after reading the install script; no network `curl | sh` execution unreviewed.
- Prove the pipeline end-to-end on a trivial law (`x = x`), run `--verdict`, record versions.
- **Stop condition:** if the toolchain cannot be built reproducibly on macOS (darwin 25) within budget, produce a Budget Stop Report and end the spike.

### Wave A — Model + laws + proofs

- `formal/bend/policy-lifecycle/`: `Model.bend`, `LAWS.bend` (Captain-reviewed, protected), `Proofs.bend`.
- Prove P1–P6; `--verdict` passes.
- **Law integrity rule:** `LAWS.bend` changes require Captain review; CI compares it against `main` (Bend’s “gates come from main” pattern).

### Wave B — Conformance, mutation tests, evidence

- Export script + differential test (pytest style used in `tests/`).
- Mutation suite proving harness rejects broken models/tables.
- Evidence record schema + writer; opt-in `northstar formal check`.
- Add `docs/integrations/` page and `TESTING.md` section; skip-when-absent behavior tested.

### Wave C — Report & decision gate

- `docs/plans/BEND_POLICY_PROOF_SPIKE.md` results + `.agent/evidence/bend-policy-proof-spike/report.json`.
- ADR in `DECISIONS.md` recording the go / no-go and boundary of what proofs do and do not guarantee.
- Update `PROGRESS.md`, `CHANGELOG.md`, `PROJECT_CONTEXT.md` (experimental, optional dependency).

## Decision Gate (measured, not asserted)

Record and report:

| Metric | Why |
|---|---|
| Wall time + effort to build toolchain | Adoption cost |
| Proof authoring effort (iterations) | Maintenance cost |
| Proof/check runtime in CI | Gate cost |
| Mutations caught / mutations injected (target 100%) | Harness value |
| Real defects or ambiguities found in `states.py` / `promote.py` | Added value over existing tests |
| Spec-to-code gap items (what the model cannot cover) | Honest boundary |

**Go** (propose follow-up plan for planner-graph or evidence-gate proofs): all properties proved, 100% mutation rejection, conformance exhaustive pass, and either ≥1 real finding or demonstrably lower review cost than tests alone.  
**No-go:** archive spike as docs/evidence; remove nothing from production; keep the CI “gates from main” idea as a separate small item.

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Proof ≠ production code | Differential exhaustive conformance test + drift test; documented in ADR |
| Agent weakens laws to pass | `LAWS.bend` Captain-owned; compared to `main`; hash in evidence |
| Unaudited AI-written compiler / unproven parser | Use `--verdict` kernel check; mutation controls; state limits in report; never sole gate |
| Supply chain (`curl \| sh`, young repo) | Pin SHA, read script, isolated prefix, `dependency-supply-chain` Skill |
| Toolchain pain on macOS (clang/Lean) | Wave 0 stop gate; budget cap |
| Scope creep to planner/hooks | Explicit non-goals; material expansion returns to approval gate |
| Experimental code bloats default CI | Opt-in flag; skipped when Bend missing |

## Acceptance Criteria

- [ ] Wave 0 provenance review recorded; Bend pinned and built in an isolated prefix.
- [ ] P1–P6 proved; `--verdict` passes; evidence record written with hashes and versions.
- [ ] Exhaustive Python↔model conformance test passes; drift test fails when tables change unpaired.
- [ ] All injected mutations are rejected (evidence recorded).
- [ ] With Bend absent or flag unset: doctor, `tests/run.sh`, and CI behave exactly as before (skip, not fail).
- [ ] No change to `orchestrator/behavior/policy/*` runtime semantics; authority locks unchanged.
- [ ] No secrets in repo; installer/updater unchanged.
- [ ] Spike report + ADR contain the go / no-go with the measured metrics.
- [ ] `PROGRESS.md`, `TESTING.md`, `CHANGELOG.md`, `PROJECT_CONTEXT.md` updated; rollback instructions documented.

## Validation plan

- Static analysis/lint on new Python and shell; unit + integration tests (conformance, mutation, skip-when-absent).
- `./scripts/doctor.sh` and `./tests/run.sh` with and without Bend present.
- Security review (supply chain, command execution of compiler, path handling) via `security-reviewer`; adversarial review focused on law-weakening and model/code mismatch.
- Not applicable: browser screenshots, accessibility, deployment smoke (no UI/deploy).
- Rollback review: remove `formal/`, opt-in CLI command, docs; revert to `rollback/pre-bend-policy-proof-spike`.

## Post-approval process (per governance)

1. ✅ Approval recorded (2026-11-18); status **APPROVED**.
2. ✅ Issue #278 created.
3. ✅ Rollback tag and `feature/278-bend-policy-proof-spike` worktree created from `main`.
4. Implement Wave 0 → A → B → C with cohesive commits `<type>(<scope>): <summary> (#278)`.
5. Validate, adversarial review, update docs, open PR. Merge remains Captain-only.

## Decisions on Open Questions (resolved at approval)

1. Q1 — Replace root `IMPLEMENTATION_PLAN.md` with this plan.
2. Q2 — Policy lifecycle only; planner task-graph validator deferred.
3. Q3 — Isolated project-local toolchain prefix (git-ignored).
4. Q4 — Default budget (3 plan iterations, 8 implementation loops, $25, 6 h).
5. Q5 — `LAWS.bend` is Captain-reviewed on every change.

## Amendments (post-implementation review, 2026-11-18)

Recorded in the open after an adversarial and a security review of the implementation. None
changes production semantics, adds a dependency, or widens authority. **A1 narrows a proof claim
and is flagged for explicit Captain review.**

- **A1 — P4/P5 are per-step, not per-sequence (scope narrowing).** The approved text said
  "arbitrary sequences". Implemented: P4 and P5 are proved for every accepted *step* over all
  inputs; P3 (terminal) **is** proved over arbitrary sequences (P3′), and P9 proves `run` unfolds
  one step at a time. Lifting P4/P5 to whole histories needs a transitivity lemma over stage
  ordering, which in Bend 2 means hand-written rewrites (no tactics). **Not proved;** it is a
  declared gap, not a hidden one.
- **A2 — Evidence gates are in the conformance grid.** The approved text abstracted them as
  booleans. They remain abstracted, but the exhaustive differential grid now covers all 16
  evidence combinations (1568 rows) so restrictive-direction mutants are detectable.
- **A3 — Added laws P7a–d, P8a/b, P9a/b, P10** (evidence gates; `next` is rejection-stable and
  acceptance-lands; `run` agrees with `next`; outcome agrees with `decide`), plus a
  Captain-owned `SPEC.bend` of independent observers so a mutated model cannot satisfy the laws
  vacuously.
- **A4 — Conformance bridge reads the real code.** The Python reference calls the real
  `can_transition` / `require_captain_approved` and extracts the gate structure of `promote_policy`
  via `ast`; both are pinned in `tables.lock.json` (drift lock) together with a law manifest.
  Gate *order* is pinned by the lock, **not proved**.
- **A5 — Hardening:** fail-closed law-integrity check (`--strict-laws --base-ref`), bad ref is an
  error, files absent at base count as changed; environment allowlist, process-group timeout,
  output clip and optional `COMPASS_BEND_SHA256` pin for the compiler; the opt-in gate is enforced in
  library entry points, not only the shell wrapper.
- **A6 — Filename:** the agent-written proof file is `PROOF.bend` (generated by `gen_proof.py`).
- **A7 — Finding H2 (outside the model):** `ensure_policy_for_instruction` trusts an instruction's
  `approval_state`, so a policy can be created directly in `proven` with no Captain approval or
  evidence. Authority flags stay false. Reported with a live repro; **no production fix**
  (out of scope). Evidence: `.agent/evidence/bend-policy-proof-spike/finding-001-direct-entry-bypass.md`.
- **A8 — CI wiring of the law-integrity comparison is deferred** until the go/no-go decision;
  until then the check is a manual/opt-in command.

## Rollback

Spike is additive and opt-in. Revert the PR, or reset to tag `rollback/pre-bend-policy-proof-spike`. Isolated toolchain prefix can be deleted without side effects.
