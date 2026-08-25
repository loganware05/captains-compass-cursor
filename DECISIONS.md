# Decisions

## ADR-028: Live OpenAI-compatible embeddings, live package-registry TI, soft-hook skip-env (v1.16.0 M12)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M11 shipped fixture embeddings and file package-registry TI. Captains
  need opt-in live embedding HTTP and live npm/PyPI discovery without CI network.
  Soft-hook skips needed durable env inheritance when Cursor does not forward
  process env (ADR-015 follow-up beyond ADR-016 command-string/marker).
- **Decision:**
  1. Ship `OpenAICompatibleEmbeddingProvider` behind
     `COMPASS_EMBEDDING_PROVIDER=openai-compatible` using
     `COMPASS_EMBEDDING_API_KEY` / `BASE_URL` / `MODEL` (never commit keys).
  2. CI tests use mocked HTTP only; defaults remain `tfidf` / stub TI.
  3. TF-IDF remains fallback on missing dense index or live embed failure.
  4. Ship `PackageRegistryLiveTechnologyIntelligenceProvider` behind
     `COMPASS_TI_PROVIDER=package-registry` for npm + PyPI (Captain local).
  5. Soft hooks honor `.agent/compass-skip.env` (`COMPASS_SKIP_*=1` lines;
     gitignored) in addition to process env, command-string, and marker file.
  6. Extend Skills `embedding-providers` and `package-registry-ti` (no new Skills).
  7. Hosted vector DBs remain deferred.
- **Consequences:** Captain-local live semantic search and package discovery;
  CI stays offline-safe; soft-hook skips work without Cursor env forwarding.

## ADR-027: Fixture embedding protocol and package-registry file TI (v1.15.0 M11)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M6 shipped TF-IDF vector search; M10 deferred production embeddings
  and package-registry TI. Captains need opt-in dense search and package discovery
  without live HTTP in CI.
- **Decision:**
  1. Ship `EmbeddingProvider` protocol with **fixture-only** dense backend
     (`COMPASS_EMBEDDING_PROVIDER=fixture`); default remains TF-IDF (`tfidf`).
  2. Dense index at `.agent/knowledge/embedding-index.json`; explicit rebuild via
     `rebuild-knowledge-embedding-index.sh`.
  3. **TF-IDF always remains fallback** when dense index missing or provider is
     `tfidf`.
  4. No OpenAI-compatible / live embedding HTTP in M11.
  5. Ship `PackageRegistryFileTechnologyIntelligenceProvider` behind
     `COMPASS_TI_PROVIDER=package-registry-file` (npm/PyPI-shaped fixtures).
  6. Dedicated Skills `embedding-providers` and `package-registry-ti` (38 Skills).
  7. Hosted vector DBs and live registry scrapers remain deferred.
- **Consequences:** Semantic search can opt into dense fixture vectors safely;
  package signals enter TI plans; CI/default stub TI + TF-IDF unchanged.

## ADR-026: External knowledge ingest and Hugging Face file TI (v1.14.0 M10)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** Notion architecture lists Notion, NotebookLM, and Hugging Face as
  TI/knowledge sources. M9 deferred file-export ingest and broader TI providers.
  Live MCP/Hub calls must stay out of CI.
- **Decision:**
  1. Ingest Captain-exported Notion/NotebookLM markdown via explicit CLI
     (`--from-store notion,notebooklm`) into `kind: knowledge` with provenance
     `export_mode: file` (no live MCP pull).
  2. Ship `HuggingFaceFileTechnologyIntelligenceProvider` behind
     `COMPASS_TI_PROVIDER=huggingface-file` (fixtures / local export; no Hub
     network in CI).
  3. TI Stars cache envelope includes `fetched_at` (and legacy `refreshed_at`);
     `refresh-ti-cache.sh --if-stale HOURS` skips network when fresh.
  4. New Skill `external-knowledge-ingest` (36 Skills); extend
     `knowledge-steward` and `technology-intelligence-live`.
  5. Production embeddings and package-registry TI remain deferred.
- **Consequences:** External research becomes durable and queryable; HF signals
  enter candidate promotion; CI/default stub TI unchanged.

## ADR-025: Skill promotion lifecycle completion and Artifact Context (v1.13.0 M9)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M3 capped candidate promotion at `SANDBOX_TESTED`. Notion §9 item 9
  calls for a full Skill promotion lifecycle. Plans lacked **Artifact Context**
  for the fifth knowledge form.
- **Decision:**
  1. Extend candidate stages through `APPROVED` → `AVAILABLE_SKILL` → `PROVEN_SKILL`.
  2. Require `--captain-approved` for all stages after `SANDBOX_TESTED`.
  3. `AVAILABLE_SKILL` writes install **proposals** under
     `.agent/capabilities/candidates/available-proposals/` — never auto-install
     into `.cursor/skills/`; never set `approved_for_execution: true`.
  4. `PROVEN_SKILL` requires ≥2 successful Experiences referencing the skill slug
     (override via `COMPASS_PROVEN_SUCCESS_THRESHOLD`).
  5. Plan writer always renders **Artifact Context** (`kind: artifact`).
  6. New Skill `skill-lifecycle` (35 Skills); `candidate-promotion` remains the
     pre-sandbox path.
  7. Notion MCP / NotebookLM ingest and production embeddings remain deferred.
- **Consequences:** Candidates can graduate to proven maturity under Captain
  control; Artifact knowledge becomes planning-visible; CI/default stub TI
  unchanged.

## ADR-024: Procedure knowledge ingest and offline TI cache (v1.12.0 M8)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M5 shipped procedure promotion staging but playbooks were not
  ingested as queryable `kind: procedure` knowledge. M7 shipped live Stars TI
  but deferred offline cache. Plans lacked **Procedure Context** readback.
- **Decision:**
  1. Ingest `playbook.md` from **staging** and **approved** procedure roots via
     explicit CLI (`--from-store procedures`); idempotent `know-proc-*` keys.
  2. Plan writer always renders **Procedure Context** (empty when no matches).
  3. Ship `./scripts/refresh-ti-cache.sh` and separate
     `COMPASS_TI_PROVIDER=github-stars-cached` reading
     `.agent/intelligence/ti-cache/starred-repos.json`.
  4. New Skill `procedure-playbooks` (34 Skills total); extend knowledge-steward
     and technology-intelligence-live.
  5. Production embedding APIs and Notion MCP ingest remain deferred.
- **Consequences:** Third Notion knowledge form becomes planning-visible;
  local TI reuse without repeated gh calls; CI/default stub unchanged.

## ADR-023: Performance knowledge ingest and live GitHub Stars TI (v1.11.0 M7)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M6 deferred performance-knowledge enrichment and live Technology
  Intelligence. Execution runs ingested as `kind: artifact` with minimal metrics;
  TI remained stub/file-only. Captains need execution-quality readback in plans
  and optional live discovery from starred repos without CI network calls or
  auto-executing external code.
- **Decision:**
  1. Map `ExecutionRun` and enriched `Experience` ingest to **`kind: performance`**
     with optional `performance_metrics` (explicit CLI only; re-ingest overwrites
     `know-run-*` / `know-exp-*` idempotently).
  2. Plan writer always renders **Performance Context** (empty when no matches);
     informational only — no matcher weight changes.
  3. Ship `GithubStarsTechnologyIntelligenceProvider` behind
     `COMPASS_TI_PROVIDER=github-stars` (starred repos only via `gh api user/starred`);
     fail closed without `gh auth`; CI/default remains `stub`.
  4. Golden-recorded fixtures for mapper tests; `./scripts/query-technology-intelligence.sh`
     for explicit Captain queries.
  5. Extend `knowledge-steward` and `candidate-promotion` Skills; add
     `technology-intelligence-live` Skill (33 Skills total).
- **Consequences:** Execution telemetry joins the unified knowledge layer;
  live TI is Captain-gated and demoable locally; safety invariants from M2–M6
  preserved. See
  [`docs/integrations/technology-intelligence.md`](docs/integrations/technology-intelligence.md).

## ADR-020: Persistent-role promotion and bounded Level 3 weight apply (v1.8.0 M4)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M3 records proficiency and routing proposals but cannot graduate
  specialists or close the learning loop into matcher weights. Architecture
  calls for persistent roles and Stage 3 autonomy without unsupervised self-mod.
- **Decision:**
  1. Persistent-role promotions write **staging drafts + proposals only**;
     landing under `.cursor/agents/` requires a Captain-reviewed PR (no
     `--captain-approved` filesystem copy into live agents).
  2. Matcher weights live in `orchestrator/matcher/weights.json` with defaults
     identical to historical hard-coded `WEIGHTS`.
  3. Bounded Level 3 apply requires `captain_approved: true` on each routing
     proposal, autonomy-budget weight-apply headroom, and an eval gate; audit
     under `.agent/routing/applied/`. `auto_apply` remains `false`.
  4. Assembler may prefer Captain-approved proficient / registry persistent
     roles when reference profiles already exist; staging drafts never override.
  5. Knowledge Steward remains deferred to **M5**.
- **Consequences:** Learning loop can update rankings under explicit Captain
  control; specialist graduation is reviewable via PR; rankings stay
  deterministic at default weights.

## ADR-022: TF-IDF vector Experience store with hybrid knowledge search (v1.10.0 M6)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M5 shipped keyword-only Knowledge Steward with a NoOp
  `VectorIndexAdapter`. Semantic recall misses related items with low token
  overlap. ADR-021 deferred production vector DB to M6+.
- **Decision:**
  1. Ship stdlib **TF-IDF sparse vector index** at
     `.agent/knowledge/vector-index.json` via `FileVectorIndexAdapter`.
  2. Query supports `keyword`, `vector`, and **`hybrid`** modes; CLI default
     remains `keyword`; plan writer uses **hybrid** when vector index exists.
  3. Vector rebuild is **explicit CLI only** (`rebuild-knowledge-vector-index.sh`
     and `ingest-knowledge.sh --rebuild-vector`).
  4. Missing vector index → vector/hybrid modes degrade to keyword results.
  5. Production embedding APIs and vector DBs remain deferred; adapter boundary
     preserved for future providers.
  6. Performance-knowledge ingest deferred to **M7**.
- **Consequences:** Planning gains semantic recall without CI network deps;
  keyword index remains authoritative fallback; hybrid scores stay informational.

## ADR-021: Knowledge Steward with stdlib keyword index (v1.9.0 M5)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M1–M4 produce Experiences, evaluations, routing artifacts, and
  markdown ADRs but no unified queryable knowledge layer. Notion architecture
  defines Knowledge Steward and five knowledge forms.
- **Decision:**
  1. Ship `orchestrator/knowledge/` with ingest, keyword index, query, and
     procedure promotion proposals under `.agent/knowledge/`.
  2. Ingestion is **explicit CLI only** — no workstream-close hooks.
  3. Auto-ingest **ADR headings** from `DECISIONS.md` when ingest CLI processes
     that file or `--from-store decisions`.
  4. Capability plans gain informational **Knowledge Context** (no ranking changes).
  5. `VectorIndexAdapter` stub only; production vector DB deferred to M6+.
  6. Procedure promotion = staging + Captain PR only.
  7. Ship Skill + subagent `knowledge-steward`.
- **Consequences:** Planning can surface durable project knowledge with
  provenance; CI stays stdlib-only; vector search remains optional future work.

## ADR-001: Separate control repository

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Workflow rules must not be contaminated by product-specific code.
- **Decision:** Captain's Compass lives in its own GitHub template repository and is installed into product repos via scripts.
- **Consequences:** Product context stays in product repos; workflow updates are versioned centrally.

## ADR-002: Version 0.1 is deliberately minimal

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Full autonomy (hooks, MCP, overnight tasks, every framework) increases failure surface area.
- **Decision:** V0.1 includes five rules, seven Skills, eight agents, templates, install/doctor, one example, and installer tests only.
- **Consequences:** Tech modules, hooks, and MCP arrive in later versions after sandbox proof.

## ADR-003: Approval gate before product changes

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Agents must not implement before the Captain agrees on scope and approach.
- **Decision:** Agents may discover and plan freely; they must not modify product implementation files until IMPLEMENTATION_PLAN.md status is APPROVED with an approval record.
- **Consequences:** Slightly slower start; much safer autonomous execution after approval.

## ADR-004: Local issue/PR fallback when GitHub is unavailable

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Sandbox validation showed the workflow can create branches, rollbacks, and tests without GitHub auth, but cannot open remote PRs.
- **Decision:** When GitHub auth/MCP is unavailable, use a documented local issue placeholder and a PR-ready description. Do not treat missing remote PR creation as a workflow failure.
- **Consequences:** Real issues/PRs require authenticated `gh` and/or GitHub MCP (Stage 1 docs/Skill added in V0.2).

## ADR-005: V0.2 adds GitHub Stage 1, React/Playwright Skills, and first hooks

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** V0.1 sandbox passed; design sequence calls for GitHub → Playwright → hooks → React module next.
- **Decision:** Ship V0.2.0 with `github-integration`, `react-engineering`, `playwright-browser-validation`, and the first three hooks (secrets, protected branch, plan approval). Keep hooks fail-open (`failClosed: false`) initially.
- **Consequences:** Stronger enforcement without freezing work if a hook misbehaves; remaining hooks and tech modules deferred to later versions.

## ADR-006: V0.3 adds Node and Postgres/Prisma Skills

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Design roadmap versions Node + PostgreSQL/Prisma as v0.3.0 after React/Playwright.
- **Decision:** Add `node-engineering` and `postgres-prisma` Skills plus integration docs and an illustrative Prisma example schema. Keep them as Skills (not always-on rules).
- **Consequences:** Agents load backend/data guidance only when relevant; production DB access remains approval-gated and out of default agent context.

## ADR-007: Complete the seven-hook safety set in V0.3.1

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Design Part 10 lists seven hooks; V0.2 shipped the first three after sandbox proof.
- **Decision:** Add branch-name, pre-commit formatting, pre-push tests, and PR evidence hooks with fail-open defaults and skip env vars (`COMPASS_SKIP_FORMAT`, `COMPASS_SKIP_TESTS`, `COMPASS_SKIP_PR_EVIDENCE`). Resolve target repos via cwd/`cd` helpers.
- **Consequences:** Stronger local enforcement without freezing cross-repo agent work; skip valves for intentional overrides.

## ADR-008: V0.4 adds Docker and cloud preview Skill

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Design roadmap versions Docker and cloud previews as v0.4.0 after Node/Prisma.
- **Decision:** Add `docker-cloud` Skill focused on containers and preview/staging deploys. Production destructive actions remain Captain-approved and out of default autonomy.
- **Consequences:** Agents can containerize and document preview deploys without gaining production release authority.

## ADR-009: V0.5 adds Linear and Notion MCP Skills without moving approval out of the repo

- **Status:** Accepted
- **Date:** 2026-07-11
- **Context:** Design MCP stages 3–4 cover Linear and Notion after GitHub/Playwright.
- **Decision:** Ship `linear-integration` and `notion-integration` Skills plus setup docs. Repository plans/decisions remain authoritative; Linear/Notion are coordination and research surfaces.
- **Consequences:** Agents can use MCP when configured; offline fallbacks remain valid.

## ADR-010: V0.6 adds Python/ML Skill and explicit Cloud MCP Stage 5 limits

- **Status:** Accepted
- **Date:** 2026-07-11
- **Context:** Design tech-module order places Python/ML after Docker; MCP Stage 5 covers cloud platforms.
- **Decision:** Add `python-ml` Skill plus Stage 5 docs that keep production cloud actions Captain-approved. Also document stacked-PR landing onto `main`.
- **Consequences:** Agents gain ML guidance without expanding production cloud autonomy; release PRs must target `main`.

## ADR-011: V0.7 adds iOS engineering Skill without embedding a full Xcode app

- **Status:** Accepted
- **Date:** 2026-07-11
- **Context:** Design tech-module order places iOS after Python/ML.
- **Decision:** Ship `ios-engineering` Skill and a lightweight example placeholder. Full Xcode projects remain in product repos.
- **Consequences:** Agents get iOS guidance via Skills; the control repo stays free of product app binaries.

## ADR-012: V1.0.0 is the first stable reusable workflow release

- **Status:** Accepted
- **Date:** 2026-07-11
- **Context:** Core gate, hooks, GitHub Stage 1, and major tech Skills are proven; template repo is live.
- **Decision:** Ship 1.0.0 with safe `update.sh` / `uninstall.sh`, upgrading docs, release checklist, and Postgres MCP Stage 6 guidance. Updates still refuse to clobber product memory docs.
- **Consequences:** Product repos can upgrade workflow packages predictably; further modules remain additive minor/major releases.

## ADR-013: V1.1.0 adds Micky-inspired Skills; opensrc is preferred-optional

- **Status:** Accepted
- **Date:** 2026-07-28
- **Context:** Podcast/agentic-engineering tactics (source-as-context, post-feature cleanup, review-fix loops) complement Compass’s control plane. [opensrc](https://github.com/vercel-labs/opensrc) automates dependency source fetch/cache.
- **Decision:** Ship three Skills (`source-code-context`, `code-structure-cleanup`, `review-fix-loop`) as v1.1.0. Prefer opensrc when installed; fall back to Captain-approved `reference/repos/` paths. Do not require opensrc for doctor/install. Code-structure cleanup that touches product files always requires a **separate** approved `IMPLEMENTATION_PLAN.md`.
- **Consequences:** Agents get clearer tactical playbooks without expanding always-on rules; product repos remain usable without the opensrc CLI.

## ADR-014: Critical hooks are fail-closed; autonomy budgets are ledger-backed (v1.2.0)

- **Status:** Accepted
- **Date:** 2026-07-30
- **Context:** ADR-005 kept all hooks fail-open while the harness matured. Production
  harness practice requires safety sensors that do not silently degrade. Autonomy
  budgets existed in design/templates but lacked a Skill and on-disk ledger.
  Control-repo regressions had no CI gate.
- **Decision:**
  1. Set `failClosed: true` for `secret-protection`, `protected-branch`, and
     `plan-approval-check`. Keep soft hooks (`branch-name-validation`,
     `pre-commit-formatting`, `pre-push-tests`, `pr-evidence-validation`)
     fail-open.
  2. Ship `autonomy-budget` Skill, Markdown ledger + Budget Stop Report templates,
     installer `.agent/budgets/` layout, and a one-line always-on pointer in the
     validation rule. Budget enforcement remains agent-procedural (Cursor does not
     expose spend/iteration counters to hooks).
  3. Add control-repo GitHub Actions CI running `doctor.sh` and `tests/run.sh`.
  4. Ship as minor version **1.2.0**. This supersedes the fail-open stance of
     ADR-005 **for critical hooks only**.
- **Consequences:** Safer default deny when critical hooks fail; product repos
  gain budget templates on install/update; PRs to this control repo get automated
  harness checks. Soft-hook friction remains opt-out via existing `COMPASS_SKIP_*`
  env vars.

## ADR-015: P1 phase commands, evidence matrix, multi-runtime pointers (v1.3.0)

- **Status:** Accepted
- **Date:** 2026-07-30
- **Context:** Operators re-entered phases via free-form chat; evidence expectations
  were unstructured; teams compose Cursor with Claude Code / Codex.
- **Decision:**
  1. Ship six Cursor slash commands as thin Markdown prompts wrapping existing
     Skills (approval gate unchanged).
  2. Add `docs/EVIDENCE_MATRIX.md` and wire plan/TESTING/hooks docs to it; keep
     PR-evidence hook soft/fail-open.
  3. Keep `AGENTS.md` canonical; install thin `CLAUDE.md` only when missing;
     document multi-runtime composition without policy forks.
- **Consequences:** Clearer phase entry points and validation expectations;
  Claude Code users get a pointer without overwriting custom `CLAUDE.md`.
  Soft-hook `COMPASS_SKIP_*` env inheritance remains a deferred follow-up.

## ADR-016: P2 evals, harness GC, sessions, supply-chain, soft-hook skips (v1.4.0)

- **Status:** Accepted
- **Date:** 2026-07-30
- **Context:** Production harness practice needs deterministic sensors, drift GC,
  light observability, supply-chain caution, and soft-hook skips that work when
  Cursor does not forward shell environment variables to hook processes.
- **Decision:**
  1. Ship `tests/evals/run.sh` (deterministic) + manual sandbox behavioral checklist;
     no LLM-in-CI.
  2. Add `harness-gc` and `dependency-supply-chain` Skills; young-package thresholds
     are **labeled guidance** only.
  3. Human session notes under `.agent/sessions/`; machine traces under `.agent/runs/`.
  4. Soft hooks honor env, command-string `COMPASS_SKIP_*=1`, or `.agent/COMPASS_SKIP_HOOKS`.
  5. Add structural-test examples under `examples/structural-tests/`.
- **Consequences:** Stronger regression signal and clearer agent procedures without
  expanding always-on rules; Captains retain judgment on young dependencies.

## ADR-019: Evaluator, experience routing proposals, and dual promotion ceilings (v1.7.0 M3)

- **Status:** Accepted
- **Date:** 2026-08-24
- **Context:** M2 records Experiences but does not influence routing. Candidate
  promotion stopped at ANALYZED. Architecture calls for a Captain Compass
  Evaluator and experience-based scheduling without Level 3 autonomy.
- **Decision:**
  1. Ship Skill + CLI `compass-evaluator` / `run-evaluation.sh` and Cursor
     subagent `.cursor/agents/compass-evaluator.md` for bounded experiments
     under `.agent/evaluations/`.
  2. Experience-based routing writes **proposals only**
     (`auto_apply: false`); matcher `WEIGHTS` never mutate from proposals in M3.
  3. Candidate lifecycle ceiling is `SANDBOX_TESTED` (evidence-gated
     `SECURITY_REVIEWED` / `SANDBOX_TESTED`). Live Skills still need Captain PR.
  4. Separate Captain-approved **subagent proficiency / classification** metadata
     under `.agent/agents/proficiency/` tracks proficiency after Skill training —
     not silent persistent-role promotion.
- **Consequences:** Learning loop becomes readable and reviewable; rankings stay
  deterministic by default; subagent proficiency is auditable.

## ADR-018: Execution telemetry, file TI, and Experience dual-path (v1.6.0 M2)

- **Status:** Accepted
- **Date:** 2026-08-23
- **Context:** Milestone 1 left `ExecutionRun` unpopulated, Technology Intelligence
  as an empty stub, and candidate promotion as documentation only. Captains need
  post-execution learning without enabling live Stars APIs in CI or auto-executing
  external candidates.
- **Decision:**
  1. Write schema-valid `ExecutionRun` + `Experience` artifacts via
     `orchestrator/telemetry/` and `scripts/record-execution-run.sh` at workstream
     close (`execution-telemetry` Skill). Runtime JSON under `.agent/experience/`
     is gitignored; commit Experience samples in **control-repo tests/fixtures**
     by default.
  2. Ship Skill `experience-skill-training`: import an Experience from a product
     repo → draft Skill under control-repo staging → run control-repo tests →
     Captain-approved PR only (never auto-land into `.cursor/skills/`).
  3. Add `FileTechnologyIntelligenceProvider` behind `COMPASS_TI_PROVIDER=file`
     (default remains `stub`). Fixtures are **redacted Stars-shaped** offline
     samples — no live network TI in CI.
  4. Candidate promotion advances `DISCOVERED → ANALYZED` and may open a
     **Captain-approved Skill sidecar PR**; `approved_for_execution` stays
     `false`; never auto-merge or auto-execute.
- **Consequences:** Planning can learn from closed workstreams; TI is demoable
  offline; promotion remains Captain-gated. See
  [`docs/integrations/technology-intelligence.md`](docs/integrations/technology-intelligence.md).

## ADR-017: Skill capability metadata uses sidecar files (v1.5.0 M1)

- **Status:** Accepted
- **Date:** 2026-08-19
- **Context:** Milestone 1 requires machine-readable capability metadata on Compass
  Skills. Metadata could live in extended `SKILL.md` frontmatter or a separate file.
  Skills must remain backwards compatible with Cursor loading, `doctor.sh`, and
  install/update directory copies.
- **Decision:**
  1. Add optional `capability.yaml` sidecar alongside each Skill directory
     (`.cursor/skills/<slug>/capability.yaml`).
  2. Keep `SKILL.md` frontmatter limited to `name` and `description`.
  3. Registry compiler treats sidecar as authoritative when present; otherwise
     infers minimal metadata with a warning (`provenance.inferred: true`).
  4. Enforce `capability.id` equals Skill frontmatter `name` at compile time.
  5. Extract reference agent routing metadata to
     `orchestrator/reference-profiles/*.json` — do not bloat agent Markdown
     frontmatter.
  6. Reject hybrid frontmatter + sidecar dual-authoring (single source of truth).
- **Consequences:** Clean separation of procedure vs routing; safe validation;
  install/update unchanged; M1 ships sidecars for all 24 control-repo Skills.
  See [`docs/design/CAPABILITY_METADATA_SIDECAR_VS_FRONTMATTER.md`](docs/design/CAPABILITY_METADATA_SIDECAR_VS_FRONTMATTER.md).
