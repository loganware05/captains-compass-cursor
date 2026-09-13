# Implementation Plan — M28 Code Reviewer specialist composition

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING_APPROVAL** |
| Plan ID | `m28-reviewer-specialist-composition` |
| Supersedes | `m27-northstar-code-reviewer` (CLOSED — shipped as v1.30.0 / M27) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.30.0` / `origin/main` (M27 merged) |
| Prepared | 2026-09-13 |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track B / **B1** |
| Product dry-run target | `loganware05/bitcoin-data-collector` (context only; evidence under control/sandbox) |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.31.0** |
| Rollback tag | `rollback/pre-m28-reviewer-specialist-composition` (created after approval) |
| Branch | `cursor/m28-reviewer-specialist-composition-3b10` |
| Issue | GitHub issue (create after approval; tracker = GitHub only) |
| Captain | Logan Ware |

## Captain locks (binding — carry forward + M28)

1. **Hermetic CI** — fixture / deterministic specialist emitters only; **no model calls** on the default path
2. **Skill slug** — orchestrator Skill remains `code-reviewer` (specialists compose *into* it)
3. **No GitHub review posting** — still Phase B / M30; evidence-only reports
4. **Tracker** — GitHub issues only (Linear = flight recorder)
5. **No Star clone/exec** from Learning Loop during this plan
6. **Sandbox-first dry-run**; bitcoin-data-collector is product context / demo target, not execution of external Stars

## Request (Captain-level)

Proceed with **M28 — Code Reviewer specialist composition (roadmap B1)**: stop relying on bare monolithic heuristics alone; wire **security / adversarial / testing** specialist emitters so they produce candidate JSON that feeds the existing **verify → report** gate.

## Problem statement

1. M27 shipped `detect → investigate → verify → report` with fixture candidates and a single `generate_heuristic_candidates` path.
2. Roadmap B1 exit criterion: *“Wire security/adversarial/test Skills to emit candidate JSON into verify”* and *“Enriched mode documented; bitcoin-style dry-run is the default demo.”*
3. Today, Skill names (`security-review`, `testing-validation`) and agents (`security-reviewer`, `adversarial-reviewer`) exist as prose, but the pipeline does **not** compose them as structured candidate sources.
4. Without composition, bitcoin-style dry-runs stay thin and Learning Loop Skills cannot cleanly feed the reviewer later (A3).

## Desired outcomes (M28)

```
diff / paths / plan
        ↓
 Detect (domains + intent)  [existing]
        ↓
 Investigate (context pack) [existing]
        ↓
 Specialist composition (NEW)
   ├─ security emitter  → candidates[]
   ├─ adversarial emitter → candidates[]
   └─ testing emitter → candidates[]
   (+ optional baseline heuristics / fixtures)
        ↓
 Verify / Judge (existing confidence + evidence gates)
        ↓
 Evidence report only (.agent/evidence/code-review/<run-id>/)
 provenance.candidates_source includes specialist mix
```

### Deferred (non-goals for v1.31.0)

- GitHub PR review posting (M30 / B3)
- Intent pack installer templates (M29 / B2)
- FIND→FIX repair loop (B4)
- Precision / TP-FP reputation ledger (B5 / A3)
- Live LLM specialist calls (optional future flag; not default; not CI)
- Mutating bitcoin-data-collector product code

## Acceptance criteria

1. New module(s) under `orchestrator/review/` (e.g. `specialists.py` + thin per-specialty helpers) implement **hermetic** emitters for:
   - `security-review`
   - `adversarial-reviewer` (agent-aligned; Skill prose may map to adversarial checks)
   - `testing-validation`
2. Pipeline default (when no `--candidates` fixture) **composes** specialist candidates (union + stable id namespacing) then runs existing `verify_findings`.
3. CLI / `northstar review` supports an explicit mode flag, e.g. `--candidates-mode specialists|heuristics|fixtures` (fixtures via existing `--candidates` path); **default = specialists** (roadmap: enriched mode is the demo default).
4. Report provenance records `candidates_source` accurately (e.g. `specialists`, `specialists+heuristics`, `fixtures`).
5. Unit tests cover: each emitter produces expected ids on fixture diffs; composition dedupes; verify still discards noise; schema-valid report.
6. Docs: `docs/integrations/code-reviewer.md` + `code-reviewer` Skill procedure updated for specialist composition.
7. Doctor still lists `code-reviewer`; add checks only if new required files are introduced.
8. Sandbox (and/or control) dry-run evidence under `.agent/evidence/m28-reviewer-specialist-composition/` including a **bitcoin-style** enriched demo (reuse prior M27 bitcoin context pack / diff fixtures where possible — no product-repo mutation required).
9. Memory docs: `DECISIONS.md` ADR-045, `PROGRESS.md`, `CHANGELOG.md`, `VERSION` → **1.31.0**.
10. Default posture unchanged: **no auto-merge**, **no GitHub review posts**, **no model in CI**.

## Architecture

```
scripts/run-code-review.sh / northstar review
        │
        ▼
orchestrator/review/pipeline.py
        │
        ├─ detect.py / investigate.py          (unchanged behavior)
        ├─ specialists.py                      (NEW composition facade)
        │     ├─ security_emitter(...)
        │     ├─ adversarial_emitter(...)
        │     └─ testing_emitter(...)
        ├─ candidates.py                       (retain fixtures + optional heuristics)
        ├─ verify.py / report.py               (minor provenance fields only)
        └─ schemas/code-review-report.schema.json (extend enum/notes if needed)
```

### Specialist emitter rules (hermetic)

| Specialist | Skill / agent affinity | Example hermetic signals (deterministic) |
|---|---|---|
| Security | `security-review` / `security-reviewer` | Secret assignment, AWS key patterns, auth path without tests, `except Exception` swallow near auth, credential path under worktree |
| Adversarial | `adversarial-reviewer` | Plan non-goal / AC contradiction, missing rollback mention when deploy paths change, over-broad catch, “tests pass for wrong reason” markers (assert True / empty tests) |
| Testing | `testing-validation` | Production paths changed with no test paths; missing failure-path tests for client/HTTP modules; snapshot-only edits without assert |

Emitters **must not** call models, clone remotes, or post to GitHub. They only read the context pack + detection + local file snippets already gathered by investigate.

### Composition policy

1. If `--candidates PATH` → fixtures only (CI hermetic golden path preserved).
2. Else if `--candidates-mode heuristics` → legacy M27 heuristics only (escape hatch).
3. Else (**default `specialists`**) → run all three emitters; optionally merge residual baseline heuristics behind an internal flag or `--candidates-mode specialists+heuristics` if needed for parity tests.
4. Prefix candidate ids: `sec-…`, `adv-…`, `test-…` for provenance clarity.
5. `skills_invoked` / `skills_suggested` in the report must list the specialists actually composed.

## Implementation steps (after approval only)

1. Create GitHub issue + rollback tag `rollback/pre-m28-reviewer-specialist-composition`.
2. Implement `orchestrator/review/specialists.py` (+ tests/fixtures for specialist diffs).
3. Wire `pipeline.py` + CLI flag(s); keep fixtures path for CI.
4. Update schema/report provenance if required (backward compatible).
5. Update Skill/agent docs (`code-reviewer`); cross-link security/testing/adversarial.
6. Run `./scripts/doctor.sh`, `./tests/run.sh`, orchestrator unit tests.
7. Produce sandbox/control dry-run evidence (bitcoin-style demo).
8. Adversarial review of the change; update ADR/PROGRESS/CHANGELOG/VERSION.
9. Open PR to `main`; Captain merge → tag **v1.31.0**.

## Validation plan

| Layer | How |
|---|---|
| Static | `doctor.sh`; schema validate reports |
| Unit | New `tests/orchestrator/test_m28_specialists.py` (+ extend M27 pipeline tests) |
| Integration | `run-code-review.sh` against fixture repo + sandbox dry-run |
| Security | Confirm no secrets in evidence; redact path still applied |
| Accessibility | N/A (no UI) |
| Production build | N/A (control template repo) |
| Deployment smoke | Doctor + unit suite green on PR |
| Rollback | `git reset --hard rollback/pre-m28-reviewer-specialist-composition` / revert PR |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Specialist noise | Keep verify gate; severity/confidence floors; discard empty-evidence findings |
| Scope creep into LLM calls | Explicit lock: hermetic default; model path remains hard-error unless future plan |
| Duplicate findings vs heuristics | Namespaced ids + composition mode separation |
| Touching product repos | Dry-run evidence only; no bitcoin product commits in this plan |

## Budget

After approval: `.agent/budgets/m28-reviewer-specialist-composition.md`

Soft stop: AC + tests + evidence + PR. Hard stop: no GitHub posting; no model-in-CI; no product-repo code changes.

## Rollback

1. Revert the M28 PR or reset to rollback tag.
2. Confirm `northstar review` still runs M27 fixture/heuristic path.
3. VERSION/CHANGELOG note if tag already cut.

## Approval gate

**No product implementation until Captain explicitly approves this `IMPLEMENTATION_PLAN.md`.**

Suggested approval phrase:

`I approve IMPLEMENTATION_PLAN.md for m28-reviewer-specialist-composition`

Optional lock confirmations to include:

- hermetic specialists (no model in default path)
- no GitHub review posting
- default candidates mode = specialists
- GitHub issue tracker only
