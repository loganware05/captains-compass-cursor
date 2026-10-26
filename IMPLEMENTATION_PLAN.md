# Implementation Plan — N4 Cross-Stack Benchmark

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `n4-cross-stack-benchmark` |
| Issue | *(placeholder — create after approval)* |
| Baseline | **v1.74.1** @ `db17050` (#242 merged) |
| Branch | `cursor/n4-cross-stack-benchmark-010c` |
| Rollback | `rollback/pre-n4-cross-stack-benchmark` *(tag after approval)* |
| Proposed release | **v1.75.0** |
| Track | `consolidation/N4` |
| Captain | Logan Ware |
| Created | 2026-10-26 |
| Sources | `NorthStar_Repository_State_2026-10-24.pdf` (N4 proposal); N3 scorecard (v1.73.0) |

## Approval record

| Field | Value |
|---|---|
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-10-26 |
| Notes | Explicit: “Approve, proceed with N4”. Defaults accepted (evaluate-only; 15 tasks; seed 20261026; COMPASS_N4_BENCHMARK_ENABLED). |

---

## Request

Run a **randomized baseline vs evidence-informed** NorthStar benchmark across **three independent product stacks**, with held-out tasks, logging **cost, latency, accuracy, and security** — without auto-promoting Skills/policies or authorizing Level 3.

## Problem Statement

N3 proved hermetic Adaptive Intelligence metrics and recommended **defer** Level 3. Hermetic fixtures do **not** establish productivity gains on real independent repositories. N2 was a single sandbox lifecycle proof. Operators need a bounded, reproducible **cross-stack** experiment before N5 routing feedback or any Level 3 spend.

## Desired Outcome

1. Gated control-repo harness: `northstar benchmark n4` / `run-n4-benchmark.sh`
   (`COMPASS_N4_BENCHMARK_ENABLED` or `--enable-gates`)
2. Task pack of **12–18** independent tasks across difficulty strata (easy / medium / hard), each with matched **baseline** and **evidence-informed** variants
3. Three verified target stacks (see Current-State Analysis):
   - `loganware05/TrapHouseKitchen` — order-status style tasks (TypeScript; NorthStar installed)
   - `loganware05/Verdant.sys` — plant/data-validation style tasks (Python; **may lack NorthStar install** — verify or substitute)
   - `loganware05/bitcoin-data-collector` — idempotent recovery tasks (Python; NorthStar installed; default branch may be feature branch)
4. Frozen model/tool configuration recorded in every run report
5. Scorecard JSON schema with primary + secondary outcomes and uncertainty notes
6. Hermetic CI mode (fixtures only) + optional live mode (Captain-provided local clones / `--repo` paths)
7. Evidence under `.agent/evidence/n4-cross-stack-benchmark/`
8. Docs/ADR/CHANGELOG **v1.75.0**; N5 remains a **separate** plan; Level 3 stays **DEFERRED**

## Acceptance Criteria

- [ ] Fail-closed without `COMPASS_N4_BENCHMARK_ENABLED` / `--enable-gates`
- [ ] Schema-validated N4 report: primary outcome + secondaries + authority locks (`auto_applied` / `authority_mutation` / `approved_for_execution` / `policy_promoted` all **false**)
- [ ] ≥12 task definitions with difficulty strata; deterministic seed for randomization
- [ ] Matched baseline vs evidence-informed variants per task (same acceptance tests)
- [ ] Hermetic fixture run completes in CI/doctor smoke without cloning external repos
- [ ] Live mode documents required clone paths; refuses silent clone/execute of starred/external repos beyond Captain-listed targets
- [ ] Metrics recorded: accepted/total, estimated cost, latency, first-pass tests, review precision (when available), retries, Skill reuse, retrieval precision, security regression flag
- [ ] Held-out task subset scored separately; uncertainty / transfer notes present
- [ ] Doctor + unit tests; security review recorded
- [ ] No Skill/policy auto-promotion; no Level 3 GPU; no secrets in evidence
- [ ] CHANGELOG / VERSION / ADR for **v1.75.0**

## Non-Goals

- N5 Skill-fit / routing auto-application (proposal docs only if signal appears)
- Specialized Model Level 3 / paid large-GPU training
- Mutating product application code inside candidate repos as part of the harness itself (tasks may be **dry-run / evaluate-only** unless Captain separately approves live implement-and-PR mode)
- Claiming production productivity gains beyond the measured pilot sample
- Installing Open UI into product repos
- Closing Captain GitHub issues automatically

## Assumptions

1. PDF “Verdant AI” maps to GitHub `loganware05/Verdant.sys` (verified 2026-10-26).
2. First ship prioritizes **harness + hermetic fixtures + offline scoring**; live runs against the three stacks are opt-in with explicit `--repo` / path map.
3. “Evidence-informed” means NorthStar Cognitive Core / Experiences / Skill ranking / brain context enabled; “baseline” means those gates off or stubbed (same tools otherwise).
4. Cost may be **estimated** (token/proxy units) when live LLM billing APIs are unavailable — method must be documented in the report.
5. `bitcoin-data-collector` default branch is currently `cursor/kalshi-live-decision-system` — pin a Captain-approved ref for the pilot.

## Open Questions (defaults proposed)

| # | Question | Proposed default |
|---|---|---|
| 1 | Live implement-and-PR into product repos? | **No** for v1.75.0 — evaluate / plan / assess / review-only unless Captain sets `COMPASS_N4_LIVE_IMPLEMENT=1` and approves separately |
| 2 | Verdant.sys without NorthStar install? | Prefer `update.sh`/`install.sh` dry documentation path; if blocked, substitute `captain-compass-sandbox` as stack C and note substitution |
| 3 | Task count | **15** tasks (5 per stack), difficulty 5/5/5 across easy/medium/hard globally |
| 4 | Randomization seed | `--seed` default `20261026`; recorded in report |
| 5 | Release | **v1.75.0** |
| 6 | Gate name | `COMPASS_N4_BENCHMARK_ENABLED` |
| 7 | bitcoin-data-collector ref | Pin `main` if present else Captain-named SHA; refuse floating default feature branch without pin |

## Current-State Analysis

| Stack | Verified (2026-10-26) | Notes |
|---|---|---|
| TrapHouseKitchen | TypeScript; `.cursor/` + AGENTS present; pushed 2026-09-07 | Strong N4 candidate (order status) |
| Verdant.sys | Python; **no** `.cursor/` at root listing; pushed 2025-12-11 | Needs install or sandbox substitute |
| bitcoin-data-collector | Python; NorthStar files present; default branch **not** `main` | Pin ref; idempotent recovery tasks |
| captain-compass-sandbox | TypeScript; N2 evidence exists | Fallback / control stack |
| Control repo | v1.74.1; N3 adaptive scorecard hermetic | Reuse patterns; do not overload N3 schema |

## Proposed Architecture

```
northstar benchmark n4 [--mode hermetic|live] [--seed N] [--enable-gates]
        │
        ▼
┌─────────────────────┐     task pack JSON      ┌──────────────────────┐
│ orchestrator/       │ ◄────────────────────── │ tests/fixtures/n4/   │
│ benchmark/n4/       │                         │ tasks/*.json         │
└─────────┬───────────┘                         └──────────────────────┘
          │
          ├─ baseline arm (evidence gates off)
          └─ evidence arm (brain/assess/Experiences on)
                    │
                    ▼
          schema-validated N4Report → .agent/evidence/n4-cross-stack-benchmark/
```

**Authority:** Report is proposal/observe only. Never writes APPROVED plans, never promotes Skills/policies, never merges.

### Primary outcome

\[
\text{accepted\_tasks} / (\text{inference\_cost\_units} + \text{engineering\_cost\_units})
\]

Subject to `security_regression == false` and no authorization bypass.

### Secondary outcomes

first-pass test rate · review precision · difficulty calibration · Skill reuse · retrieval precision · retries · latency (p50/p95) · held-out transfer delta

## Required Capabilities / Reusable Capabilities

From `./scripts/capability-plan.sh --plan-id n4-cross-stack-benchmark`:

| Skill | Role |
|---|---|
| `capability-planning` | Task packs / manifests |
| `compass-evaluator` | Bounded experiment comparison |
| `testing-validation` | Hermetic + doctor |
| `security-review` | No auth regression |
| `execution-telemetry` | Run/Experience artifacts |
| `autonomy-budget` | Iteration limits |
| `repository-discovery` | Stack verification |
| `pull-request-preparation` | Closeout docs |

**TI candidates:** stub — **NOT APPROVED FOR EXECUTION**.

## Task Graph

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| `task-discovery` | Confirm stack refs, install state, pin SHAs | — | no |
| `task-architecture` | N4 schema, arms, metrics, rollback | task-discovery | no |
| `task-impl-harness` | `orchestrator/benchmark/n4` + CLI + fixtures | task-architecture | no |
| `task-impl-packs` | 15 task definitions (5×3 stacks) | task-architecture | yes |
| `task-validation` | Doctor, unit, hermetic smoke, security | task-impl-harness, task-impl-packs | no |
| `task-documentation` | ADR, CHANGELOG v1.75.0, INDEX, TESTING | task-validation | no |

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| discovery | `repository-scout` | `repository-discovery`, `capability-planning` |
| architecture | `architecture-agent` | `compass-evaluator`, `capability-planning` |
| harness | `implementation-agent` | `testing-validation`, `autonomy-budget` |
| packs | `implementation-agent` | `capability-planning` |
| validation | `test-engineer` + `security-reviewer` | `testing-validation`, `security-review` |
| documentation | `documentation-agent` | `pull-request-preparation` |

## Workstreams

### WS0 — Stack verification & pins

1. Record SHAs for TrapHouseKitchen, bitcoin-data-collector (pinned ref), Verdant.sys or sandbox substitute.
2. Document NorthStar install state per stack; propose install only with Captain ack for Verdant.
3. Exit: `STACKS.md` evidence table checked in under evidence dir.

### WS1 — Schema & harness

1. Add `n4-benchmark-report.schema.json` with authority locks.
2. Implement `orchestrator/benchmark/n4/` (`enabled`, `tasks`, `runner`, `metrics`, `service`).
3. CLI: `scripts/run-n4-benchmark.sh` + `northstar benchmark n4`.
4. Hermetic mode loads `tests/fixtures/n4/` only.
5. Exit: fail-closed doctor check + unit tests.

### WS2 — Task packs (12–18)

1. Author 15 JSON tasks: objectives, acceptance checks (hermetic stubs), difficulty, stack id, held-out flag.
2. Matched variants: `arm=baseline|evidence` with identical acceptance.
3. Seeded shuffle for presentation order; arms always paired for scoring.
4. Exit: fixture schema validation; ≥2 held-out tasks.

### WS3 — Metrics & compare

1. Compute primary/secondary metrics; baseline vs evidence deltas.
2. Emit uncertainty notes (sample size, stack substitution, cost proxy method).
3. Optional: feed summary into Open UI scorecard emitter (non-blocking).
4. Exit: compare report validates; `policy_promoted: false`.

### WS4 — Docs & release

1. ADR-095, CHANGELOG, VERSION **1.75.0**, TESTING, docs/INDEX, docs/plans/N4_*.md.
2. PROGRESS: N4 complete; N5 next (separate).
3. Rollback tag `rollback/pre-n4-cross-stack-benchmark`.
4. Exit: Definition of Done.

## Files Expected to Change (post-approval)

| Path | Change |
|---|---|
| `orchestrator/benchmark/n4/**` | New harness |
| `orchestrator/schemas/n4-benchmark-report.schema.json` | Schema |
| `scripts/run-n4-benchmark.sh`, `scripts/northstar`, `scripts/doctor.sh` | CLI + doctor |
| `tests/fixtures/n4/**`, `tests/orchestrator/test_n4_*.py` | Fixtures + tests |
| `docs/plans/N4_CROSS_STACK_BENCHMARK.md`, `DECISIONS.md`, `CHANGELOG.md`, `VERSION`, `TESTING.md`, `docs/INDEX.md`, `PROGRESS.md`, `PROJECT_CONTEXT.md` | Memory |
| `.agent/evidence/n4-cross-stack-benchmark/**`, `.agent/budgets/n4-cross-stack-benchmark.md` | Evidence + budget |

## Testing Strategy

| Layer | Artifact |
|---|---|
| Doctor | fail-closed N4 gate |
| Unit | task load, seed determinism, metric math, schema locks |
| Hermetic e2e | `northstar benchmark n4 --mode hermetic --enable-gates` |
| Security | no secret leakage; live mode path allowlist |
| Rollback | tag + revert instructions |

## Security Notes

- Never clone arbitrary starred repos; only Captain-listed stack paths.
- Evidence scrubbed of tokens/keys.
- Live implement mode default **off**.
- Authority locks in schema (const false) for promotion/auto-apply fields.

## Accessibility Review

N/A for harness-only (no new interactive UI required). If Open UI emission added, reuse existing a11y patterns.

## Migration Plan

Additive gated CLI. N3 adaptive scorecard unchanged.

## Deployment Plan

Control-repo merge + tag **v1.75.0**. Live stack runs are operator-local.

## Rollback Plan

1. Revert to `rollback/pre-n4-cross-stack-benchmark`.
2. Operators omit `benchmark n4`; N3/Open UI unaffected.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Verdant lacks NorthStar | Substitute sandbox; record in report |
| Floating bitcoin feature branch | Require `--pin-ref` / STACKS.md SHA |
| Cost unknowable without LLM bills | Document proxy units; never invent invoice data |
| Scope creep into product PRs | Default evaluate-only; live implement gated |
| Over-claiming transfer | Separate held-out section + uncertainty |

## Evaluation Strategy

- Hermetic determinism (same seed → same arm assignment)
- Schema authority locks cannot be true
- Adversarial review before merge
- Live results (if any) labeled non-CI

## Learning Plan

Retain fixtures + reports under `.agent/evidence/n4-cross-stack-benchmark/` and `.agent/plans/n4-cross-stack-benchmark/`. N5 may consume deltas as **proposals only**.

## Autonomy Budget

| Limit | Value |
|---|---|
| Maximum iterations | 10 |
| Maximum failed validation cycles | 3 |
| Maximum estimated cost | Low for hermetic; live LLM spend requires Captain cost ack |
| Budget ledger | `.agent/budgets/n4-cross-stack-benchmark.md` *(after approval)* |
| On limit | `.agent/evidence/n4-cross-stack-benchmark/BUDGET_STOP_REPORT.md` |

## Definition of Done

- Acceptance Criteria checked
- Hermetic benchmark green in CI/doctor path
- Security evidence recorded
- Docs/VERSION/CHANGELOG updated
- Rollback tag exists
- First Mate inspected
- Plan → **COMPLETE** only after merge

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Reply **approve** / **proceed with N4** (or revise open questions) to unlock WS0–WS4.

## Related follow-ups (out of scope)

- **N5** — Skill-fit / routing proposals from N4 (no auto-promotion)
- **Model proof** — adapter vs retrieval/hosted (separate cost approval)
- **Level 3** — only after demonstrated benefit + separate plan
