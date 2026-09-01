# Changelog

## Unreleased

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
