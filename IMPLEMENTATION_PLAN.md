# Implementation Plan — AHF-P01 / AI Hedge Fund Intake + Read-Only Adapter

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `ahf-p01-intake-adapter` |
| Linear | [OVA-62](https://linear.app/ovaltechnologysolutions/issue/OVA-62/ahf-p01-ai-hedge-fund-intake-read-only-northstar-adapter) · Project [P-OVA-5](https://linear.app/ovaltechnologysolutions/project/northstar-on-chain-ai-hedge-fund-67b1475ea115) |
| Spec sources | [On-Chain Intelligence Integration](https://app.notion.com/p/3efe6a901c4381d38d6eccdb85c5899c) · [Existing Systems Utilization Map](https://app.notion.com/p/3efe6a901c438145aacfce97e28fc7a1) |
| Prerequisite | **v1.49.0** on `main` (M49 merged #187 @ `b007dc4`) |
| Supersedes | Active plan was M49 (complete). Does **not** supersede deferred **M50** Policy/instruction promotion |
| Product | **NorthStar** (control repo `captains-compass-cursor`) |
| Baseline | **v1.49.0** @ `b007dc4` |
| Prepared | 2026-10-04 |
| Proposed release | **v1.50.0** |
| Rollback | Tag `rollback/pre-ahf-p01-intake-adapter` @ `b007dc4` (create after approval) |
| Proposed branch | `cursor/ahf-p01-intake-adapter-8613` |
| Captain | Logan Ware |

## Request

Start the NorthStar × Jev × AI Hedge Fund workstream by executing **Phase 0
(repository intake)** and **Phase 1 (read-only NorthStar adapter)** from the
utilization map — reusing Technology Intelligence, adapter contracts, and
approval gates already shipped in the control repo.

## Next-steps analysis (why this slice)

| Horizon | Work | Repo | Why now / later |
|---|---|---|---|
| **Now (this plan)** | Pin/inventory `ai-hedge-fund` + TI candidate + read-only adapter | `captains-compass-cursor` | Proves integration boundary before blockchain or Jev complexity |
| Next plan (AHF-P02) | Jev shadow for agent/strategy selection or signal triage | control repo | DecisionProvider M41–M45 already exists; needs hedge-fund question packs only after adapter I/O is stable |
| Later (AHF-P03) | One on-chain metric family (e.g. BTC exchange netflow) | `bitcoin-data-collector` | Collector already stubs exchange flows; keep crypto plane separate from equity runtime |
| Later (AHF-P04+) | On-chain analyst agent, portfolio experiments, behavioral feed | control + BTC + AHF | Requires P01–P03 evidence; feed M46–M49 ledgers without granting authority |

**Do not start with on-chain or live Jev.** The utilization map’s recommended first
sprint is boundary + provenance first; blockchain benefit must be isolatable.

## Problem Statement

NorthStar has orchestration, TI discovery, DecisionProvider/Jev, and behavioral
evaluation — but no governed seam to an investment research / paper-trading
runtime. Without a pinned, researched, read-only adapter:

1. Agents may reconstruct hedge-fund workflows ad hoc (no provenance)
2. `ai-hedge-fund` cannot be treated as a replaceable domain capability package
3. Later Jev triage and on-chain features have no stable run/manifest contract
4. Live-broker paths cannot be systematically forbidden at the NorthStar boundary

## Desired Outcome

```
Pinned ai-hedge-fund SHA (research-only)
  → TI CandidateCapability (approved_for_execution: false)
  → orchestrator/integrations/ai_hedge_fund/ read-only adapter
  → create_research_run / run_backtest / run_paper_session (fixture or subprocess)
  → get_market_state / get_portfolio_state / get_decision_ledger / compare_runs
  → run manifests under .agent/evidence/ahf-p01-intake-adapter/
  → feature flag COMPASS_AHF_ADAPTER_ENABLED (default off)
  → hard deny of live-broker / real-money execution surfaces
```

## Decision Summary

| Principle | Implication |
|---|---|
| Research / paper only | No live broker, wallet, or signing APIs exposed |
| Thin adapter | NorthStar does not import every AHF internal module; replaceable boundary |
| TI first | Domain package registered as candidate; never auto-executable Skill |
| Hermetic CI | File/fixture provider default; no network to Financial Datasets in CI |
| Fail closed | Missing pin, flag off, or policy violation → abstain / error; no silent live path |
| Parallel to Behavioral Loop | Track ID **AHF-P01**; do not consume deferred M50 Policy-promotion slot |
| Captain authority | Plan approval required; adapter never sets `approved_for_execution` |

## Acceptance Criteria

- [ ] Architecture inventory + dependency/SBOM notes for pinned AHF commit under `.agent/evidence/ahf-p01-intake-adapter/intake/`
- [ ] TI fixture (and optional live path docs) registers AHF with capabilities such as financial-research-orchestration, paper-portfolio-management, historical-backtesting; `approved_for_execution: false`
- [ ] Package `orchestrator/integrations/ai_hedge_fund/` with `adapter.py`, `schemas.py`, `capabilities.yaml`, `policy.py`, `evaluators.py`, `README.md`
- [ ] Schemas for run requests/results and run manifests (repo SHA, data sources, agents, model versions, instruction hashes, results)
- [ ] Operations: `create_research_run`, `run_strategy_agents` *(stub/fixture ok)*, `get_market_state`, `get_portfolio_state`, `run_backtest`, `run_paper_session`, `get_decision_ledger`, `compare_runs`
- [ ] `policy.py` hard-denies live execution; unit tests prove deny path
- [ ] Env gate `COMPASS_AHF_ADAPTER_ENABLED` default off; CI stays hermetic
- [ ] Hermetic unit/integration tests for schemas, policy, fixture adapter
- [ ] Docs: `docs/integrations/ai-hedge-fund.md` + PROGRESS/CHANGELOG/DECISIONS updates
- [ ] Rollback tag documented; uninstall/disable = unset flag + revert merge

## Non-Goals

- Jev hedge-fund question packs or DecisionProvider surface changes (AHF-P02)
- BTC exchange-flow / Glassnode integration (AHF-P03 in `bitcoin-data-collector`)
- On-chain analyst Skill/agent (AHF-P04)
- Portfolio experimentation program or paper-trading capital (AHF-P05)
- Behavioral ledger coupling beyond recording adapter evidence paths (AHF-P06)
- Real-money trading, brokers, wallets, transaction signing
- Vendoring the entire AHF UI or rewriting AHF strategies inside NorthStar
- Activating Policies, mutating `.cursor/`, or promoting Skills to AVAILABLE/PROVEN

## Assumptions

1. AHF remains an external pinned dependency (fork or commit SHA), not a full monorepo merge.
2. First executable surfaces can be **fixture-backed** if live AHF CLI requires secrets; live optional path is Captain-local only.
3. Financial Datasets / other AHF API keys never enter prompts or git.
4. Capability planner may misfire domains (e.g. prisma/react); human task graph below is authoritative.
5. `bitcoin-data-collector` continues as the crypto/on-chain plane in a later plan.

## Open Questions (Captain)

**Resolved 2026-10-04** — Captain: "I approve" + answers below.

| # | Decision |
|---|---|
| 1 | Release **v1.50.0** for AHF-P01 |
| 2 | Documented SHA + optional local path (no submodule) |
| 3 | New Linear project **NorthStar On-Chain / AI Hedge Fund** — also tracks `bitcoin-data-collector` milestones |
| 4 | Separate plan for on-chain work — **yes, on the existing `bitcoin-data-collector` repo** (AHF-P03) |
| 5 | `run_strategy_agents` — **fixture-only in v1** |

## Current-State Analysis

### Already available (reuse)

- Technology Intelligence provider boundary + `CandidateCapability` schema
- Integration adapter patterns under `orchestrator/integrations/`
- DecisionProvider / Jev (M41–M45) for a **later** phase
- Behavioral Intelligence (M46–M49) for **later** outcome learning
- Approval gates, evidence dirs, SBOM/dependency-supply-chain Skill

### Missing (this plan)

- AHF pin + intake evidence
- AHF TI fixture/candidate
- `orchestrator/integrations/ai_hedge_fund/` package
- Run/manifest schemas and hermetic tests
- Integration doc + feature flag

### Related product repo (out of scope)

- `bitcoin-data-collector` already has partial on-chain schema + Blockchain.com metrics; exchange flows still stubbed

## Proposed Architecture

```text
orchestrator/integrations/ai_hedge_fund/
├── adapter.py          # public ops; selects fixture|local provider
├── schemas.py          # pydantic/dataclass + JSON schema exports
├── capabilities.yaml   # TI-facing capability ids
├── policy.py           # deny live-broker; require research mode
├── evaluators.py       # compare_runs metrics helpers (deterministic)
├── fixtures/           # hermetic backtest/paper/ledger samples
└── README.md

docs/integrations/ai-hedge-fund.md
orchestrator/providers/technology_intelligence/fixtures/…ahf….json
.agent/evidence/ahf-p01-intake-adapter/
```

**Policy invariants (code, not model):**

- `mode ∈ {research, paper, backtest}` only
- Any request with `live`, `broker`, `sign`, `wallet` → hard deny
- Adapter outputs always `approved_for_execution: false`

## Required Capabilities

Human-corrected (capability-plan inferred unrelated prisma/react noise):

- python-service-development
- api-contract-definition / schema design
- technology-intelligence candidate registration
- dependency-supply-chain review
- unit-test-execution / definition-of-done-validation
- security-review (secrets, live-path deny)
- documentation / github-pr

Machine artifact: `.agent/plans/ahf-p01-intake-adapter/resolve.json`

## Reusable Capabilities Found

| Skill | Role in this plan |
|---|---|
| `technology-intelligence-live` / file TI | Register AHF candidate (file fixture default) |
| `dependency-supply-chain` | SBOM / young-dependency review of AHF pin |
| `python-ml` | Patterns for eval/backtest harnesses (light touch) |
| `security-review` | Secret boundaries + live-deny tests |
| `testing-validation` | Hermetic unit/integration evidence |
| `notion-integration` | Spec provenance (already linked) |
| `github-integration` / `pull-request-preparation` | Issue OVA-62 + PR |

## Technology Intelligence Candidates

> External candidates are **NOT APPROVED FOR EXECUTION**.

| Candidate | Path | Notes |
|---|---|---|
| `virattt/ai-hedge-fund` | https://github.com/virattt/ai-hedge-fund | Primary domain runtime for this track; pin SHA in intake evidence |

During implementation, add an offline Stars-shaped / TI fixture so CI can surface the candidate without network.

## Task Graph

Authoritative human graph (overrides machine frontend-oriented default):

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| `task-discovery` | Inventory AHF surfaces, APIs, deps; choose pin SHA | — | no |
| `task-architecture` | Finalize adapter contracts, schemas, policy deny list | task-discovery | no |
| `task-ti-fixture` | Add TI fixture + capabilities.yaml mapping | task-architecture | yes |
| `task-adapter-impl` | Implement fixture provider + policy + ops | task-architecture | yes |
| `task-validation` | Unit/integration tests, doctor if needed, security review | task-ti-fixture, task-adapter-impl | no |
| `task-documentation` | Integration doc, ADR, PROGRESS, CHANGELOG, evidence | task-validation | no |

## Proposed Agent Configuration

| Task | Profile | Skills |
|---|---|---|
| `task-discovery` | `repository-scout` | `repository-discovery`, `source-code-context`, `dependency-supply-chain` |
| `task-architecture` | `architecture-agent` | `capability-planning`, `dependency-supply-chain` |
| `task-ti-fixture` | `implementation-agent` | `technology-intelligence-live`, `python-ml` |
| `task-adapter-impl` | `implementation-agent` | `python-ml`, `code-structure-cleanup` |
| `task-validation` | `test-engineer` + `security-reviewer` | `testing-validation`, `security-review` |
| `task-documentation` | `documentation-agent` | `pull-request-preparation`, `notion-integration` |

## Workstreams

1. **Intake & pin** — fork/pin decision, inventory, SBOM notes
2. **TI registration** — fixture + docs; never executable
3. **Adapter + policy** — hermetic ops + live deny
4. **Validation & docs** — tests, ADR, integration guide

## Parallelization Plan

After architecture: TI fixture and adapter implementation may proceed in parallel
(disjoint files). Validation is serial after both land.

## Files Expected to Change

- `orchestrator/integrations/ai_hedge_fund/**` (new)
- `orchestrator/providers/technology_intelligence/fixtures/*ahf*` (new)
- `docs/integrations/ai-hedge-fund.md` (new)
- `docs/integrations/technology-intelligence.md` (cross-link)
- `tests/orchestrator/test_ahf_*.py` (new)
- `IMPLEMENTATION_PLAN.md`, `PROGRESS.md`, `CHANGELOG.md`, `DECISIONS.md`
- `VERSION` *(only if Captain answers Open Question 1 with a bump)*
- `.agent/evidence/ahf-p01-intake-adapter/**`
- `.agent/budgets/ahf-p01-intake-adapter.md`
- `.agent/plans/ahf-p01-intake-adapter/**` (already seeded)

## Testing Strategy

| Layer | What |
|---|---|
| Unit | Schema validation; policy deny for live modes; fixture adapter ops |
| Integration | File TI surfaces AHF candidate; compare_runs on fixtures |
| Doctor / registry | No break to compile-capability-registry / doctor |
| Security | No secrets in fixtures; live path unreachable with flag off |
| CI | Default provider fixture; no AHF network |

Evidence root: `.agent/evidence/ahf-p01-intake-adapter/`

## Security Review

- AHF API keys / Financial Datasets credentials: Captain-local env only; never commit
- Redact secrets from any captured logs/manifests
- Policy deny list for live/broker/sign/wallet
- Supply-chain review of pinned commit before any optional local invoke
- Adapter outputs cannot grant execution authority

## Accessibility Review

Not applicable (no UI).

## Migration Plan

None. Additive package + default-off flag.

## Deployment Plan

Control-repo merge only. No product-repo installer change required for P01
unless Captain requests a doc note in installed integration index.

## Rollback Plan

1. Revert merge commit or restore tag `rollback/pre-ahf-p01-intake-adapter`
2. Unset `COMPASS_AHF_ADAPTER_ENABLED`
3. Remove/ignore TI fixture if it causes plan noise (optional)

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| AHF CLI unstable / secret-heavy | Fixture-first; optional local invoke behind separate flag |
| Scope creep into on-chain or Jev | Explicit Non-Goals; separate plan IDs |
| VERSION / M50 naming collision | Open Question 1 |
| Treating TI candidate as approved Skill | Schema `approved_for_execution: false`; docs callout |
| Subprocess escape / unexpected network | Policy + hermetic tests; no network in CI |

## Evaluation Strategy

Success for P01 is **integration quality**, not portfolio return:

- Inventory completeness (executable surfaces documented)
- Adapter ops hermetic pass rate
- Live-deny test coverage
- Provenance fields present on every run manifest
- Zero CI network calls to AHF data providers

## Learning Plan

Retain under `.agent/plans/ahf-p01-intake-adapter/` and evidence root. Feed later
AHF-P02+ with stable I/O contracts. Do not auto-tune Skills from P01 alone.

## Autonomy Budget

After approval, create/update `.agent/budgets/ahf-p01-intake-adapter.md`.

| Resource | Soft | Hard |
|---|---|---|
| Implementation iterations | 3 | 5 |
| Failed validation cycles | 2 | 3 |
| Full test suite runs | 4 | 8 |
| Scope expansions without re-approval | 0 | 0 |

On limit: write `.agent/evidence/ahf-p01-intake-adapter/BUDGET_STOP_REPORT.md` and stop.

## Definition of Done

- Acceptance criteria checked
- Tests + security review evidence recorded
- Docs/ADR/PROGRESS/CHANGELOG updated
- Rollback instructions present
- Plan status → COMPLETE only after merge (or Captain stop)
- First Mate inspection complete

## Approval Boundary

**Implementation must not begin until the Captain explicitly approves this plan.**

Machine-generated capability matches and agent manifests are proposals only.
Answering the Open Questions (especially #1 VERSION and #2 pin form) should
accompany approval.

## Approval Record

| Field | Value |
|---|---|
| Approved by | Captain Logan Ware |
| Approved at | 2026-10-04 |
| Method | Explicit message: "I approve" + open-question answers 1–5 |
| Linear project | [NorthStar On-Chain / AI Hedge Fund](https://linear.app/ovaltechnologysolutions/project/northstar-on-chain-ai-hedge-fund-67b1475ea115) (P-OVA-5) |
| Linear issue | [OVA-62](https://linear.app/ovaltechnologysolutions/issue/OVA-62/ahf-p01-ai-hedge-fund-intake-read-only-northstar-adapter) |
| Plan revision | Pre-implementation approval on branch `cursor/ahf-p01-intake-adapter-8613` |
