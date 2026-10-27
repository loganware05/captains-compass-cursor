# N1 Closeout Ledger

Plan: `n1-operational-reconciliation` · Baseline: **v1.71.0** @ `c7679bf`  
Machine-readable: [`CLOSEOUT_LEDGER.json`](CLOSEOUT_LEDGER.json)

**Rule:** dispositions are proposals. Captain verifies and closes GitHub issues.
Agents must not auto-close.

| Item | Status | Recommended disposition | Key evidence |
|---|---|---|---|
| #220 Post-C7 closeout | completed | Verify → close | PR #221 / v1.66.1 |
| #222 E2E Cognitive Core | completed | Verify → close | PR #224 / v1.67.0 |
| #144 M28 specialist composition | completed | Verify → close | PR #143 |
| #146 M29 intent packs | completed | Verify → close | PR #145 / v1.32.0 |
| #147 M30 GitHub draft reviews | completed | Verify allowlist/tests → close | PR #149 / v1.33.0 |
| #169 M38 shell forge gate | completed | Verify residual → close or residual issue | PR #173 / v1.39.1 |
| #170 M39 Agentic Security Phase B | completed | Verify → close | PR #175 / v1.40.0 |
| #164 M35 product install (roadmap/C2) | completed | Close original M35; N2 revalidates current VERSION | PR #166 / v1.38.0 |
| `specialized-model-level-3` | deferred | Keep deferred until L0–2 POV + separate Captain plan | `SPECIALIZED_MODEL_LEVEL_3.md` |
| docs/INDEX drift | completed | Fixed in N1 / v1.71.1 | this PR |
| skill count 47 vs 48 | completed | Verified **47** Skills; `inodes/` is content store | this PR |
| C2 track namespace collision | completed | Documented `roadmap/*` vs `cognitive/*` | this PR |
| N2 Product Integration | completed | Shipped v1.72.0 / #239 | `docs/plans/N2_*` |
| N3 Adaptive Intelligence | completed | Shipped v1.73.0 / #240 | `docs/plans/N3_*` |
| Open UI Control Plane | completed | v1.74.0 / #241; hotfix v1.74.1 / #242 | `docs/plans/OPENUI_*` |
| N4 Cross-Stack Benchmark | completed | Shipped v1.75.0 / #243 | `docs/plans/N4_*` |
| N5 Skill-Fit / Routing Feedback | completed | Shipped v1.76.0 / #244 | `docs/plans/N5_*` |

## Release ↔ milestone traceability (v1.66+ consolidation)

| Release | Milestone |
|---|---|
| v1.66.0 | Cognitive Core C7 |
| v1.66.1 | Post-C7 closeout (#221) |
| v1.67.0 | E2E Cognitive Core (#224) |
| v1.68.0 | Read-only persistent oversight (#227) |
| v1.69.0 | Specialized Model Level 0 (#230) |
| v1.70.0 | Specialized Model Level 1 (#232) |
| v1.71.0 | Specialized Model Level 2 (#234) |
| v1.71.1 | **N1** Operational Reconciliation |
| v1.72.0 | **N2** Product Integration Validation |
| v1.73.0 | **N3** Adaptive Intelligence Validation |
| v1.74.0 | Open UI Control Plane |
| v1.74.1 | Open UI Lang string hotfix |
| v1.75.0 | **N4** Cross-Stack Benchmark |
| v1.76.0 | **N5** Skill-Fit / Routing Feedback |
