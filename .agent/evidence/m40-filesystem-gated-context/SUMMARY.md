# M40 Evidence — Filesystem-Gated Context & Dependency Architecture

Plan: `m40-filesystem-gated-context` (IMPLEMENTATION_PLAN.md, APPROVED 2026-09-18)
Branch: `cursor/m40-filesystem-gated-context-ea39` (control PR #177)
Sandbox: `captain-compass-sandbox` branch `cursor/m40-filesystem-gated-context-ea39`

## Control-repo validation

| Check | Result |
|---|---|
| `./scripts/doctor.sh` | 0 errors, 0 warnings (incl. new skill-inode freshness + schema checks) |
| `./tests/run.sh` | 125 passed, 0 failed |
| Orchestrator unit tests | 432 passed (`test_m40_*`: 35 tests across inodes/walker, skill inodes, dependency graph, boundary gate, manifest pwd) |
| `./tests/evals/run.sh` | 43 passed, 0 failed (incl. M40 sensor block) |

## Measured context-window optimization (fixture corpus)

Deterministic eval sensor 5: monolithic inode dump vs walked-route payload.

- Monolithic (all inodes + index): **9473 bytes**
- Scoped walk `src/ui` (route inodes only): **4572 bytes**
- **Reduction: 52%** on the 5-file fixture corpus; the mechanism scales with
  repo size because walk payloads are bounded by the route, not the repo.

## Sandbox validation (captain-compass-sandbox)

Workflow refresh: `update.sh` 1.28.0 → 1.40.1 (M40 control state).
Inode build over sandbox `src/`: 14 files indexed, 14 inodes, 4 context nodes.
Route walk `src/lib` resolves with real export summaries (see
`sandbox-walk-src-lib.json`).

| Command | Result |
|---|---|
| `npm run lint` (oxlint) | clean |
| `npm run test` (vitest) | 5 files, 31 tests passed (26 baseline + 5 new) |
| `npm run build` (tsc + vite) | built successfully |

Full output: `sandbox-npm-validation.txt`.

## Boundary precision (milestone lifecycle step 4)

Corpus: sandbox `main...HEAD` clean cross-boundary change
(`src/lib/formAnalytics.ts` + `src/components/FormIssuesSummary.tsx`) and a
seeded-violation diff (`seeded-violations.diff`, evidence-only, not committed
to product source).

| Run | Boundary candidates | Verified boundary findings |
|---|---|---|
| Clean change (`m40-sandbox-clean`) | **0** | 0 |
| Seeded violations (`m40-sandbox-seeded`) | **3** | 3 (all `verified`) |

Seeded violations detected (all crossing `src/components` → `src/lib`):

1. `boundary-unknown-symbol-...-purgeFormIssues` (high) — import of a symbol
   the callee inode does not export
2. `boundary-arity-...-summarizeFormIssues` (medium) — 0 args passed vs 1
   required by the declared signature
3. `boundary-complexity-...-summarizeFormIssues` (medium) — declared `O(N)`
   callee invoked inside an added loop ⇒ effective `O(N^2)`

**Boundary precision = TP/(TP+FP) = 3/3 = 1.0** on the sandbox corpus;
fixture corpus precision also 1.0 (3 TP / 0 FP, asserted in
`tests/orchestrator/test_m40_boundary_gate.py` and the M40 eval sensor).

Reports: `sandbox-clean-review-report.json`, `sandbox-seeded-review-report.json`.

## Known follow-up (observed during validation; not M40 scope)

The M37 agentic-equivalent specialist emitted one false positive
(`sec-hook-checkout-shortcircuit`, medium) on the sandbox diff because the
diff *removes* the legacy checkout short-circuit from `protected-branch.sh`
(hook refresh) — the detector matches the pattern in removed lines. Boundary
findings (M40) are unaffected. Recommend a follow-up plan: M37 detectors
should scan added lines only.
