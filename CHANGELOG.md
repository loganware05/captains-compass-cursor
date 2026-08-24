# Changelog

## Unreleased

### Added

- Milestone 6: Vector Experience Store — TF-IDF file vector index, hybrid
  keyword+vector query, `rebuild-knowledge-vector-index.sh` (extends `knowledge-steward`).

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
