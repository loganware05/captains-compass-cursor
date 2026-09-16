# Changelog

## 1.38.1 — 2026-09-16

### Fixed

- **M36 / Hook security hardening** — close two medium findings from Cursor
  Agentic Security Review on bitcoin-data-collector PR #7:
  - `plan-approval-check`: product edits require a **committed** APPROVED plan
    (table Status + real Approved by / Approval date); writing APPROVED into
    `IMPLEMENTATION_PLAN.md` needs `COMPASS_CAPTAIN_APPROVE=1` (no self-serve)
  - `protected-branch`: deny push refspecs to protected branches, honor
    `git -C`, remove `checkout -b feature/` substring short-circuit
- Hermetic tests: `tests/orchestrator/test_m36_hook_security_hardening.py`
- ADR-053

## 1.38.0 — 2026-09-16

### Added

- **M35 / C2 Product-repo install** — NorthStar install into
  `bitcoin-data-collector` proven locally (no control `scripts/` copy)
- `install.sh` rewrites bare `./scripts/` → `$CONTROL/scripts/` in product
  Skills/agents/commands/integrations after copy
- Product INDEX learn example uses `--repo "$(pwd)"`
- Evidence: `.agent/evidence/c2-product-repo-install/` (scrubbed install log,
  SHA-aligned inventory + patch for Captain push — bot lacks write access)
- ADR-052

### Locks (unchanged)

- Control `scripts/` never copied into product repos
- Product memory docs skip-if-exists
- Linear is flight recorder only
- Skill slug remains `code-reviewer`

## 1.37.0 — 2026-09-16

### Added

- **M34 / C1 Single launcher UX** — unified `northstar` help surface map for
  skills / review / intent / outcomes / repair / precision
- Operator docs index: `docs/INDEX.md` (control) + `templates/docs/INDEX.md` (product)
- Clear control vs product install boundary in `install.sh` help +
  `docs/PRODUCT_ONBOARDING.md`
- Product install skip-if-exists copies product-scoped INDEX + selected
  integration docs (never control `scripts/`)
- Doctor checks for help surfaces + INDEX/onboarding boundary
- Hermetic tests for help, control INDEX link integrity, and install boundary
- ADR-051

### Locks (unchanged)

- Control `scripts/` never copied into product repos (C2 remains separate)
- Linear is flight recorder only
- Skill slug remains `code-reviewer`
- Hermetic CI / no model on default path

## 1.36.0 — 2026-09-15

### Added

- **M33 / B5 Precision ledger** — aggregate Code Reviewer finding outcomes into
  skill/specialist precision dashboards (evidence + Experience)
- Schema `precision-ledger.schema.json` (`northstar.precision_ledger.v1`)
- Module `orchestrator/review/precision.py`
- CLI `scripts/aggregate-precision-ledger.sh` / `northstar precision aggregate`
- Optional proposal-only invocation-priority RoutingProposal
  (`--emit-priority-proposal`, min sample default 5)
- Fixture `tests/fixtures/code-review/precision-outcomes.json`
- Tests: `tests/orchestrator/test_m33_b5_precision_ledger.py`
- Evidence: `.agent/evidence/b5-precision-ledger/` +
  `.agent/evidence/precision/b5-fixture-demo/`
- ADR-050

### Locks (unchanged)

- No silent reputation mutation / no auto-apply priority
- Finding outcomes never originate Captain approval
- Linear is flight recorder only
- Skill slug remains `code-reviewer`
- Hermetic CI / no model on default path

## 1.35.0 — 2026-09-15

### Added

- **M32 / B4 Repair loop** — FIND→PROVE→packet starter for verified Code Reviewer findings
- Module `orchestrator/repair/loop.py` (verified-only, allowlist-gated, never auto-merge)
- Schema `repair-run.schema.json` (`northstar.repair_run.v1`)
- CLI `scripts/start-repair-loop.sh` / `northstar repair start`
- Fixture `tests/fixtures/repair/sandbox-report.json`
- Tests: `tests/orchestrator/test_m32_b4_repair_loop.py`
- Evidence: `.agent/evidence/b4-repair-loop/` + `.agent/evidence/repair/b4-sandbox-fixture-demo/`

### Locks (unchanged)

- Never auto-merge repair PRs
- Unverified/discarded findings refused
- Captain FIX authorization required to prepare submit metadata
- Linear is flight recorder only
- Skill slug remains `code-reviewer`

## 1.34.0 — 2026-09-15

### Added

- **M31 Finding outcomes → Experience → RoutingProposal** — record human
  triage of Code Reviewer findings as durable Experience lessons
- Schema `finding-outcome.schema.json` (`northstar.finding_outcome.v1`)
- Module `orchestrator/review/outcomes.py` (normalize, Experience write,
  optional proposal-only RoutingProposal)
- CLI `scripts/record-finding-outcomes.sh` /
  `northstar outcomes record`
- Fixture `tests/fixtures/code-review/triage-outcomes.json`
- Tests: `tests/orchestrator/test_m31_finding_outcomes.py`
- Evidence: `.agent/evidence/m31-finding-outcomes/`

### Changed

- Doctor checks for outcomes module, schema, and record script
- `code-reviewer` Skill + integration docs describe finding outcomes

### Locks (unchanged)

- Hermetic CI / no model on default path
- RoutingProposal always proposal-only (`auto_apply=false`)
- Outcomes never originate Captain approval
- Linear is flight recorder only — never Captain approval
- Skill slug remains `code-reviewer`
- No FIND→FIX repair loop (B4 deferred)
- No auto-merge / no webhooks

## 1.33.0 — 2026-09-13

### Added

- **M30 Opt-in GitHub draft reviews** — allowlist-gated PENDING draft PR reviews
- Module `orchestrator/review/github_draft.py` (never APPROVE / REQUEST_CHANGES)
- Schema `github-allowlist.schema.json` + template `.agent/review/github-allowlist.yml`
- CLI `--post-github-draft` / `--github-repo` / `--pull-number` (off by default)
- Tests: `tests/orchestrator/test_m30_github_draft.py`
- Evidence: `.agent/evidence/m30-github-draft-reviews/`

### Changed

- Code-review report schema allows `github_review_posted: true` when a draft is posted
- Doctor checks for github draft module, allowlist schema/template
- Installer creates `.agent/review/` and installs allowlist skip-if-exists
- `code-reviewer` Skill + integration docs describe opt-in draft posting

### Locks (unchanged)

- Hermetic CI / no model on default path
- Draft posting off by default; sandbox allowlist first
- Linear is flight recorder only — never Captain approval
- Skill slug remains `code-reviewer`
- No auto-merge / no webhooks

## 1.32.0 — 2026-09-13

### Added

- **M29 Intent packs + installer templates** — normalized review intent so Code
  Reviewer can run without hand-written temporary plans
- Schema `intent-pack.schema.json` (`northstar.intent_pack.v1`) + loader
  `orchestrator/review/intent.py` (`captain_approval` always false)
- CLI `--intent-json`; auto-discover `INTENT_PACK.md` / `.agent/intent/current.json`
- Optional Linear export: `scripts/export-intent-from-linear.sh` /
  `northstar intent export` (fixture-first, never approval)
- Installer template `INTENT_PACK.md` + `.agent/intent/` (skip-if-exists)
- Tests: `tests/orchestrator/test_m29_intent_packs.py`

### Changed

- `templates/docs/IMPLEMENTATION_PLAN.md` includes intent-pack sections
- `code-reviewer` Skill + integration docs describe intent packs
- Doctor checks for intent module, schema, template, and export script

### Locks (unchanged)

- Hermetic CI / no model on default path
- No GitHub review posting (M30 deferred)
- Linear is flight recorder only — never Captain approval
- Skill slug remains `code-reviewer`

## 1.31.0 — 2026-09-13

### Added

- **M28 Code Reviewer specialist composition** — hermetic security / adversarial /
  testing emitters (`orchestrator/review/specialists.py`) compose candidate JSON
  into the existing verify → report gate
- CLI `--candidates-mode specialists|heuristics|specialists+heuristics` (default:
  `specialists`); fixtures via `--candidates` remain the CI golden path
- Tests: `tests/orchestrator/test_m28_specialists.py`

### Changed

- Default code-review candidates source is specialists (M27 heuristics retained as
  escape hatch)
- `code-reviewer` Skill + integration docs describe specialist composition
- Doctor checks for `orchestrator/review/specialists.py`

### Locks (unchanged)

- Hermetic CI / no model on default path
- No GitHub review posting (M30 deferred)
- Skill slug remains `code-reviewer`

## Unreleased

## 1.30.0 — 2026-09-12

### Added

- **M27 NorthStar Code Reviewer MVP** — Detection → Investigation → Verification →
  Review pipeline (`orchestrator/review/`) with hermetic CLI
  (`scripts/run-code-review.sh`, `northstar review`)
- Schema `code-review-report.schema.json`; Skill/agent `code-reviewer`; reference profile
- Evidence-only reports under `.agent/evidence/code-review/<run-id>/` (no GitHub posts)
- Fixtures + tests: `tests/orchestrator/test_m27_code_review.py`
- Docs: `docs/integrations/code-reviewer.md`, design archive
- ADR-044; issue #141; rollback tag `rollback/pre-m27-northstar-code-reviewer`

### Changed

- VERSION `1.30.0`
- Doctor lists `code-reviewer` Skill/agent + review CLI/schema checks

## 1.29.1 — 2026-09-11

### Added

- M25 agent router wakeability gate (`orchestrator/routing/agent_router.py`,
  `northstar.agent_router.v1`) — expired/unreachable pins cannot remain
  dispatch-ready when declared `availability=1.0` (OVA-17 learning / OVA-19)
- CLI: `northstar skills route-agents` → `scripts/score-agent-routing.sh`
- Docs: `docs/integrations/agent-routing-contract.md`
- Tests: `tests/orchestrator/test_m25_agent_router_wakeability.py`
- Doctor check for `score-agent-routing.sh`
- ADR-042; evidence `.agent/evidence/m25-agent-router-wakeability/VALIDATION.md`

### Changed

- VERSION `1.29.1`
- PROGRESS: M25 marked shipped (OVA-19)

## 1.29.0 — 2026-09-11

### Added

- M24 Linear Skills Learning Loop flight recorder (H0–H3 + M0 + minimal sync)
- Topology-free launcher `scripts/northstar` (`skills refresh|learn|promote|sync-ledger`)
- Learning-run `ledger` linkage (`orchestrator/integrations/skills_ledger.py`) +
  `scripts/sync-skill-learning-ledger.sh`
- Docs: `docs/integrations/linear-skills-learning-loop.md`,
  `docs/templates/linear/northstar-skill-learning-run.md`
- ADR-041; tests `tests/orchestrator/test_m24_skills_ledger.py`
- Doctor checks for `northstar` + `sync-skill-learning-ledger.sh` executables
- Closeout evidence `.agent/evidence/m24-linear-skills-ledger/VALIDATION.md`
  (doctor/tests green; Run 001 retain via sandbox PR #46)

### Changed

- VERSION `1.29.0`
- Skills `skill-learning-loop`, `technology-intelligence-live` and guide
  `starred-repos-to-skills` lead with control/sandbox topology (`CONTROL` /
  `SANDBOX`, northstar or `--repo-root`); product checkouts do not contain
  learning CLIs
- Linear adapter allowlist includes project **NorthStar Skills Learning Loop**
- PROGRESS: M24 marked shipped; Run 001 closed retained

## 1.28.0 — 2026-09-10

### Added

- M23 TI scorecard + skill flywheel: `design-system` usefulness category
- Starred-provenance gate for external-repo TI entry (fail closed)
- Metadata-only TI scorecard writers (`security-review` +
  `dependency-supply-chain`) required before any Skill draft
- Script `example-design-repo-scorecard.sh` (categorize → scorecard → draft;
  no auto Skill install)
- ADR-040; tests `tests/orchestrator/test_m23_ti_skill_flywheel.py`
- Budget `.agent/budgets/m23-ti-skill-flywheel.md` + evidence pack

### Changed

- VERSION `1.28.0`
- Skills `skill-learning-loop`, `candidate-promotion` document M23 gates
- `apply-skill-improvement` enforces draft evidence + `--captain-approved`
- Learning loop writes scorecard evidence before drafts/proposals
- Docs: technology-intelligence, SANDBOX_VALIDATION, TESTING, PROGRESS

## 1.27.0 — 2026-09-09

### Added

- M22 NorthStar unattended live ops: injectable `HttpTransport`, sandbox product
  allowlist, stdlib GitHub webhook ingress, live adapter factory
- Scripts `serve-northstar-ingress.sh`; routine flags `--mode`, `--product-repo`
- Docs `docs/integrations/northstar-live-ops.md` + ADR-039
- Tests `tests/orchestrator/test_m22_northstar_live.py` + webhook fixtures

### Changed

- VERSION `1.27.0`
- Adapters report `mode` in healthchecks; live outbound via transport
- Live `--approve` shortcut refused (GitHub plan_digest path only)
- Doctor checks ingress script + ingress module import
- Skill `northstar-connected-routine` documents live mode

## 1.26.0 — 2026-09-08


### Added

- NorthStar ↔ M4 bridge (`orchestrator/integrations/m4_bridge.py`) for persistent-role
  propose-only and routing proposal surfacing after `REVIEW_READY` (#50)
- CLI flags `--propose-roles`, `--surface-routing`, `--notion-mode` on
  `run-northstar-routine.sh` (#50)
- Notion fixture research pack + non-authoritative summary mirror payload (#50)
- ADR-038 (#50)

### Changed

- VERSION `1.26.0`
- Skills `northstar-connected-routine`, `persistent-role-promotion`,
  `bounded-autonomy`, and `notion-integration` cross-link the bridge (#50)
- Docs clarify Notion remains research/summary only; GitHub stays approval truth

## 1.25.0 — 2026-09-08

### Added

- **NorthStar** product identity with branding registry and legacy Captain's Compass aliases (`orchestrator/branding.py`)
- Connected operating routine across Slack, Linear, GitHub, and Cursor (`orchestrator/integrations/`)
- Fixture adapters for all four providers (no live credentials in CI)
- State machine, idempotency store, reconcile helpers, and work-packet dispatch with M21 agent identity enforcement
- Scripts `run-northstar-routine.sh`, `reconcile-northstar-run.sh`
- Skill `northstar-connected-routine`
- Docs `docs/integrations/slack.md` (+ GitHub/Linear NorthStar authority notes)
- ADR-037
- Fixture pack `tests/fixtures/northstar/` + `tests/orchestrator/test_m21_northstar.py`

### Changed

- VERSION `1.25.0` (M21 NorthStar connected operations)
- Doctor skill list includes `northstar-connected-routine`
- Human-facing new output prefers NorthStar; machine IDs (repo slug, Skill paths, env vars) remain stable

## 1.24.0 — 2026-09-03

### Added

- Skill learning loop orchestrator (`run-skill-learning-loop.sh`, `orchestrator/learning/`) (#111)
- Skill `skill-learning-loop` — draft new Skills and propose improvements to similar existing Skills (#111)
- Fixture sandbox candidate harness + evidence templates (#111)
- Behavioral checklist item 9 (skill learning loop) (#111)
- Automated release smoke `skill-learning-loop-fixtures` (#111)
- ADR-035 (#111)
- Experience bridge from learning runs (`bridge-learning-experiences.sh`, `--record-experiences`) (#113)
- Captain-gated Skill improvement apply (`apply-skill-improvement.sh`) (#113)
- ADR-036 (#113)

### Changed

- VERSION `1.24.0` (includes M19 / v1.23.0 scope + M20)
- TI docs: mark M14 batch Stars ML as shipped; document M19/M20 learning loop (#111, #113)
- Skill `technology-intelligence-live` cross-links skill learning loop (#111)
- Skill `skill-lifecycle` cross-links learning-run Experiences (#113)

## 1.22.0 — 2026-09-01

### Added

- Required sandbox release smoke runner (`run-sandbox-release-smokes.sh`) (#106)
- Release closeout smoke validator (`validate-sandbox-release-smokes.sh`) (#106)
- Evidence templates under `.agent/evidence/_templates/sandbox-release-smoke/` (#106)
- Behavioral checklist item 8 (post-foundation M13–M17 fixture smokes) (#106)
- ADR-034 (#106)

### Changed

- VERSION `1.22.0`
- `docs/RELEASE_CHECKLIST.md` step 12 gates closeout on smoke evidence (#106)
- Consolidated pending sandbox validation rows (v1.6.0–v1.21.0) (#106)
- Skill `testing-validation` documents release smoke gate (#106)

## 1.21.0 — 2026-09-01

### Added

- Stage 3 context selection proposals (`propose-context-selection.sh`, `apply-context-selection-proposal.sh`) (#102)
- Decomposition hints on experience routing proposals (bounded matcher-factor deltas) (#102)
- ADR-033 (#102)

### Changed

- VERSION `1.21.0`
- Plan builder reads Captain-approved `.agent/routing/context-selection-active.json` (#102)
- Skills `bounded-autonomy` and `experience-routing` document Stage 3 paths (#102)

## 1.20.0 — 2026-09-01

### Added

- Live Hugging Face Hub TI provider (`COMPASS_TI_PROVIDER=huggingface-hub`) (#98)
- Optional `COMPASS_HF_HUB_TOKEN` for authenticated Hub requests (#98)
- ADR-032 (#98)

### Changed

- VERSION `1.20.0`
- Skill `technology-intelligence-live` documents live Hub path (#98)

## 1.19.0 — 2026-08-31

### Added

- Live Notion MCP knowledge ingest with page allowlist (`ingest-notion-live.sh`) (#94)
- Provenance `export_mode: mcp_live` for MCP-fetched Notion pages (#94)
- ADR-031 (#94)

### Changed

- VERSION `1.19.0`
- Skills `external-knowledge-ingest` and `notion-integration` document live MCP path (#94)

## 1.18.0 — 2026-08-31

### Added

- Batch GitHub Star categorization ML pipeline (`categorize-github-stars.sh`) (#89)
- `COMPASS_TI_PROVIDER=github-stars-categorized` offline TI provider (#89)
- Manual label fixtures for Naive Bayes training (#89)
- ADR-030 (#89)

### Changed

- VERSION `1.18.0`
- Skill `technology-intelligence-live` documents categorized Stars path (#89)

## 1.17.0 — 2026-08-31

### Added

- Hosted pgvector/Neon knowledge vector adapter with namespace isolation (#86)
- `COMPASS_VECTOR_PROVIDER=pgvector|mock` with explicit sync/schema CLIs (#86)
- Skill `hosted-vector-db` (39 Skills) + integration docs (#86)
- ADR-029 — Neon/pgvector over Pinecone on cost at scale (#86)

### Changed

- VERSION `1.17.0`
- Query order: hosted pgvector → file dense → TF-IDF fallback (#86)
- Hosted ranking fail-closes on misconfig/live errors (Bugbot #87) (#86)

## 1.16.0 — 2026-08-24

### Added

- OpenAI-compatible embedding provider (`COMPASS_EMBEDDING_PROVIDER=openai-compatible`,
  `COMPASS_EMBEDDING_*` env) with mocked CI tests (#82)
- Live package-registry TI (`COMPASS_TI_PROVIDER=package-registry`) for npm + PyPI (#82)
- Soft-hook skip-env inheritance via `.agent/compass-skip.env` (#82)
- ADR-028 (#82)

### Changed

- VERSION `1.16.0`
- Skills `embedding-providers` / `package-registry-ti` document live paths (#82)
- Soft-hook README documents compass-skip.env (#82)

## 1.15.0 — 2026-08-24

### Added

- Fixture `EmbeddingProvider` + dense embedding index (`COMPASS_EMBEDDING_PROVIDER=fixture`)
  with TF-IDF always as fallback (#78)
- `rebuild-knowledge-embedding-index.sh` (#78)
- `COMPASS_TI_PROVIDER=package-registry-file` offline npm/PyPI-shaped TI (#78)
- Skills `embedding-providers` + `package-registry-ti` (38 Skills) (#78)
- ADR-027 (#78)

### Changed

- VERSION `1.15.0`
- `knowledge-steward` / `technology-intelligence-live` document embedding + package TI (#78)

## 1.14.0 — 2026-08-24

### Added

- File-export Notion + NotebookLM knowledge ingest (`--from-store notion,notebooklm`) (#74)
- `COMPASS_TI_PROVIDER=huggingface-file` offline HF model-card TI (#74)
- TI cache `fetched_at` + `refresh-ti-cache.sh --if-stale <hours>` (#74)
- Skill `external-knowledge-ingest` (36 Skills) (#74)
- ADR-026 (#74)

### Changed

- VERSION `1.14.0`
- `knowledge-steward` / `technology-intelligence-live` document external ingest + HF file TI (#74)
- Stars cache envelope writes `fetched_at` (keeps `refreshed_at` alias) (#74)

## 1.13.0 — 2026-08-24

### Added

- Candidate promotion stages `APPROVED` → `AVAILABLE_SKILL` → `PROVEN_SKILL`
  with `--captain-approved` gates (#70)
- AVAILABLE_SKILL install proposals under
  `.agent/capabilities/candidates/available-proposals/` (#70)
- PROVEN_SKILL requires ≥2 successful Experiences (#70)
- Plan writer **Artifact Context** section (always rendered; empty when none) (#70)
- Skill `skill-lifecycle` (35 Skills) (#70)
- ADR-025 (#70)

### Changed

- VERSION `1.13.0`
- `promote-candidate.sh` supports post-sandbox stages + `--captain-approved` (#70)
- `candidate-promotion` Skill documents pre-sandbox ceiling; defers to
  `skill-lifecycle` for APPROVED+ (#70)

## 1.12.0 — 2026-08-24

### Added

- Procedure playbook ingest (`--from-store procedures`) → `kind: procedure` (#66)
- Plan writer **Procedure Context** section (always rendered; empty when none) (#66)
- Offline TI cache: `refresh-ti-cache.sh`, `COMPASS_TI_PROVIDER=github-stars-cached` (#66)
- Skill `procedure-playbooks` (34 Skills); extends `knowledge-steward`,
  `technology-intelligence-live` (#66)
- ADR-024 (#66)

### Changed

- VERSION `1.12.0`
- `ingest-knowledge.sh` supports `procedures` store root (staging + approved) (#66)
- `select_ti_provider()` accepts repo root for cached Stars TI (#66)

## 1.11.0 — 2026-08-24

### Added

- Performance knowledge ingest: `ExecutionRun` → `kind: performance` with
  `performance_metrics`; enriched Experience performance items (#62)
- Plan writer **Performance Context** section (always rendered; empty when none) (#62)
- Live TI: `GithubStarsTechnologyIntelligenceProvider` via
  `COMPASS_TI_PROVIDER=github-stars` (starred repos only; gh auth required) (#62)
- `query-technology-intelligence.sh` explicit TI CLI (#62)
- Skill `technology-intelligence-live` (33 Skills); extends `knowledge-steward`,
  `candidate-promotion` (#62)
- ADR-023 (#62)

### Changed

- VERSION `1.11.0`; re-ingest overwrites existing `know-run-*` as `performance` (#62)
- `knowledge-item.schema.json` optional `performance_metrics` object (#62)

## 1.10.0 — 2026-08-24

### Added

- TF-IDF file vector index (`.agent/knowledge/vector-index.json`) and
  `FileVectorIndexAdapter` (#58)
- Hybrid knowledge query: `query-knowledge.sh --mode keyword|vector|hybrid` (#58)
- `rebuild-knowledge-vector-index.sh` and `ingest-knowledge.sh --rebuild-vector` (#58)
- Plan writer **hybrid** Knowledge Context when vector index exists (#58)
- ADR-022 (#58)

### Changed

- VERSION `1.10.0`; extends `knowledge-steward` Skill (no new Skill count)
- CLI query default remains `keyword`; plan writer defaults to hybrid when index present

## 1.9.0 — 2026-08-24

### Added

- Knowledge Steward Skill + CLIs (`ingest-knowledge.sh`, `query-knowledge.sh`,
  `propose-procedure-from-knowledge.sh`); explicit CLI ingest only (#54)
- `orchestrator/knowledge/` — ingest, keyword index, query, procedure promotion
  staging; `VectorIndexAdapter` NoOp stub for M6+ (#54)
- Store layout: `.agent/knowledge/items/`, `index.json`, `ingest-log/` (#54)
- Plan writer **Knowledge Context** section (informational only) (#54)
- ADR heading auto-ingest from `DECISIONS.md` (#54)
- `knowledge-steward` subagent + reference profile (#54)
- ADR-021 (#54)

### Changed

- VERSION `1.9.0`; thirty-two Skills; ten reference agent profiles
- Install seeds `.agent/knowledge/` paths

## 1.8.0 — 2026-08-24

### Added

- Persistent-role promotion Skill + CLI (`propose-persistent-role.sh`); staging drafts
  + Captain PR only (#50)
- Bounded Level 3 autonomy: Captain-flagged routing weight apply (`bounded-autonomy`,
  `apply-routing-proposal.sh`) under autonomy budget + eval gate (#50)
- `orchestrator/matcher/weights.json` with loader; apply audit under
  `.agent/routing/applied/` (#50)
- Assembler preference for Captain-approved proficient / persistent-role agents (#50)
- ADR-020 (#50)

### Changed

- VERSION `1.8.0`; thirty-one Skills
- Install seeds `.agent/routing/applied/`, `.agent/agents/promotions/`
- Routing proposals include `captain_approved: false` by default; apply requires
  explicit Captain flag per proposal

## 1.7.0 — 2026-08-24

### Added

- Captain Compass Evaluator Skill + CLI (`run-evaluation.sh`) + `compass-evaluator` subagent (#45)
- Experience-routing proposals (proposal-only; no live matcher weight mutation) (#45)
- Candidate promotion through `SECURITY_REVIEWED` → `SANDBOX_TESTED` with evidence gates (#45)
- Captain-gated subagent proficiency / classification metadata (`record-agent-proficiency.sh`) (#45)
- Plan section **Experience Signals** (informational; does not alter rankings) (#45)
- ADR-019 (#45)

### Changed

- VERSION `1.7.0`; twenty-nine Skills; nine reference agent profiles
- Install seeds `.agent/evaluations/`, `.agent/routing/proposals/`, `.agent/agents/proficiency/`
- Registry compiler allows Skill and reference-profile ids to share names across kinds

## 1.6.0 — 2026-08-23

### Added

- Execution telemetry: `ExecutionRun` + `Experience` store, `record-execution-run.sh`, Skill `execution-telemetry` (#41)
- File Technology Intelligence provider (`COMPASS_TI_PROVIDER=file`) with redacted Stars-shaped offline fixtures (#41)
- Candidate promotion (`DISCOVERED → ANALYZED`) and Captain-gated Skill sidecar drafts; Skill `candidate-promotion` (#41)
- Skill `experience-skill-training` — import product Experience, draft Skill in control-repo staging (#41)
- ADR-018 — execution telemetry, file TI, Experience dual-path (#41)

### Changed

- VERSION `1.6.0`; twenty-seven Skills; install seeds `.agent/experience/`; close-workstream records telemetry (#41)
- `docs/integrations/technology-intelligence.md` documents file provider and promotion ceiling (#41)

## 1.5.0 — 2026-08-19

### Added

- Capability-aware planning orchestrator (`orchestrator/`) — schemas, registry compiler, intent matcher, task graph, agent manifests, plan writer (#35)
- `capability.yaml` sidecars for all Skills (ADR-017) and eight reference agent profiles (#35)
- `capability-planning` Skill, `scripts/capability-plan.sh`, and `/plan-feature` pipeline integration (#35)
- Enhanced `IMPLEMENTATION_PLAN.md` template sections: capabilities, task graph, agent configuration, TI candidates, approval boundary (#35)
- Technology Intelligence provider stub + `docs/integrations/technology-intelligence.md` (no GitHub Stars coupling) (#35)

### Changed

- VERSION `1.5.0`; doctor expects twenty-four Skills; install seeds `.agent/capabilities/compiled/` and `.agent/plans/`
- Installer copies technology-intelligence integration doc when missing
- ADR-017

## 1.4.0 — 2026-07-30

### Added

- Harness evals (`tests/evals/run.sh`) + sandbox behavioral checklist (`docs/evals/`) (#32)
- `harness-gc` Skill — drift detection across rules/Skills/commands/docs (#32)
- `dependency-supply-chain` Skill — labeled guidance for young/low-provenance packages (#32)
- Session notes: `templates/agent/SESSION_NOTE.md`, installer `.agent/sessions/` (#32)
- `examples/structural-tests/` (dependency-cruiser sample) (#32)
- Soft-hook skips via command-string `COMPASS_SKIP_*=1` or `.agent/COMPASS_SKIP_HOOKS` (#32)

### Changed

- VERSION `1.4.0`; doctor expects twenty Skills; install seeds `.agent/sessions/` (#32)
- ADR-016

## 1.3.0 — 2026-07-30

### Added

- Phase commands: `/plan-feature`, `/implement-approved-plan`, `/validate-change`, `/prepare-pr`, `/close-workstream` (#29)
- Evidence matrix (`docs/EVIDENCE_MATRIX.md`) (#29)
- Multi-runtime agent adapters doc (`docs/integrations/multi-runtime-agents.md`) (#29)
- `CLAUDE.md` template for product repos (#29)

### Changed

- VERSION `1.3.0`; doctor expects eighteen Skills (#29)

## 1.2.0 — 2026-07-30

### Added

- Autonomy budget Skill and ledger templates (#26)
- Fail-closed hooks policy documented; control-repo CI workflow (#26)
- Budget stop report procedure (#26)

### Changed

- VERSION `1.2.0`; doctor validates failClosed split (#26)
- ADR-015

## 1.1.0 — 2026-07-28

### Added

- Micky-inspired Skills: `code-structure-cleanup`, `review-fix-loop`, `source-code-context` (#19)
- Structural test example README (#19)

### Changed

- VERSION `1.1.0`; doctor expects sixteen Skills (#19)

## 1.0.0 — 2026-07-11

### Added

- Stable update/uninstall scripts with product memory preservation (#14)
- Product onboarding guide (#14)
- Release checklist and upgrading docs (#14)

### Changed

- VERSION `1.0.0`; template repository enabled (#14)

## 0.7.0 — 2026-07-11

### Added

- iOS engineering Skill and integration doc (#12)

## 0.6.0 — 2026-07-11

### Added

- Python/ML Skill and Cloud MCP Stage 5 docs (#11)

## 0.5.0 — 2026-07-11

### Added

- Linear and Notion MCP integration Skills (#8)

## 0.4.0 — 2026-07-10

### Added

- Docker/cloud deployment Skill (#6)

## 0.3.1 — 2026-07-10

### Added

- Remaining safety hooks (branch name, formatting, pre-push tests, PR evidence) (#5)

## 0.3.0 — 2026-07-10

### Added

- Node engineering and Postgres/Prisma Skills (#3)

## 0.2.0 — 2026-07-10

### Added

- GitHub integration Skill and Stage 1 live docs (#2)

## 0.1.0 — 2026-07-10

### Added

- Initial Captain's Compass control repository: rules, Skills, subagents, hooks, installer
