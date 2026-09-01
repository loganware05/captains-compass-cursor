# Technology Intelligence integration (adapter boundary)

Captain Compass consumes **normalized candidate capabilities** from external
Technology Intelligence (TI) sources. Feeds such as GitHub Star Categorization,
package registries, or internal discovery engines connect through a **provider
adapter** — never through direct repository imports or auto-execution.

## Purpose

During `/plan-feature`, the orchestrator may surface **discovery signals** that
could become future Skills or reference implementations. These are **not**
approved Compass capabilities until the Captain promotes them through review.

Approved Compass Skills (registry `kind: skill`, lifecycle `AVAILABLE_SKILL` /
`PROVEN_SKILL`) are matched separately by the deterministic resolver.

## Provider contract

**Module:** `orchestrator/providers/technology_intelligence/`

**Protocol:**

```python
class TechnologyIntelligenceProvider(Protocol):
    def discover_candidates(
        self, objective: str, context: dict
    ) -> list[CandidateCapability]: ...
```

**Inputs:**

| Field | Description |
|---|---|
| `objective` | Same natural-language objective passed to capability planning |
| `context` | Optional repo context (stacks, discovery summary, security flags) |

**Output:** Zero or more `CandidateCapability` dataclass instances. Each
`to_dict()` payload must validate against
`orchestrator/schemas/candidate-capability.schema.json`.

### Required candidate fields

| Field | Constraint |
|---|---|
| `kind` | Must be `"candidate"` |
| `approved_for_execution` | Must be `false` (schema enforces `const: false`) |
| `lifecycle_stage` | `DISCOVERED` or `ANALYZED` (M2 promotion ceiling before Captain PR) |
| `source.type` | Must be `"external-candidate"` |
| `source.path` | Opaque locator (repo URL, catalog id, etc.) — no path traversal into Compass |
| `capabilities_provided` | Non-empty list of capability ids the signal might satisfy |

Optional: `discovery_signal`, `notes`, `source.provenance_url`.

### Validation gate

`orchestrator/providers/technology_intelligence/validate.py` runs before plan
rendering. Invalid or `approved_for_execution: true` candidates **fail closed**
with `TechnologyIntelligenceValidationError`.

## Provider selection

| Env var | Values | Default |
|---|---|---|
| `COMPASS_TI_PROVIDER` | `stub` \| `file` \| `github-stars` \| `github-stars-cached` \| `github-stars-categorized` \| `huggingface-file` \| `huggingface-hub` \| `package-registry-file` \| `package-registry` | `stub` |
| `COMPASS_TI_FIXTURES_DIR` | absolute/relative path | package `fixtures/` |
| `COMPASS_EMBEDDING_PROVIDER` | `tfidf` \| `fixture` \| `openai-compatible` | `tfidf` |
| `COMPASS_EMBEDDING_API_KEY` | API key for openai-compatible | (required when live) |
| `COMPASS_EMBEDDING_BASE_URL` | OpenAI-compatible base URL | `https://api.openai.com/v1` |
| `COMPASS_EMBEDDING_MODEL` | embedding model id | `text-embedding-3-small` |
| `COMPASS_PACKAGE_TI_FIXTURES_DIR` | absolute/relative path | package `fixtures/package-registry/` |
| `COMPASS_PACKAGE_TI_ECOSYSTEMS` | `npm,pypi` | `npm,pypi` |
| `COMPASS_HF_HUB_TOKEN` | optional Hub auth token | (unset) |

`orchestrator/plan_writer/build.py` calls `select_ti_provider()`. CI and default
installs stay on **stub** (empty list). Set `COMPASS_TI_PROVIDER=file` for local
demos using redacted Stars-shaped fixtures under
`orchestrator/providers/technology_intelligence/fixtures/`. Set
`COMPASS_TI_PROVIDER=github-stars` for **live starred repos** via authenticated
`gh` (Captain local only; fails closed without auth). Set
`COMPASS_TI_PROVIDER=github-stars-cached` to read the offline cache at
`.agent/intelligence/ti-cache/starred-repos.json` (refresh via
`./scripts/refresh-ti-cache.sh`; optional `--if-stale HOURS` skips when
`fetched_at` is fresh). Set `COMPASS_TI_PROVIDER=huggingface-file` for offline
Hugging Face model-card fixtures (no Hub network in CI). Set
`COMPASS_TI_PROVIDER=huggingface-hub` for **live Hub model search** (Captain local
only; mocked HTTP in CI). Set
`COMPASS_TI_PROVIDER=package-registry-file` for offline npm/PyPI-shaped package
fixtures (no registry network in CI). Dense knowledge embeddings are separate
(`COMPASS_EMBEDDING_PROVIDER=fixture`; Skill `embedding-providers`) — TF-IDF
remains the default fallback.

Explicit read-only queries:

```bash
COMPASS_TI_PROVIDER=github-stars ./scripts/query-technology-intelligence.sh --query "react forms"
./scripts/refresh-ti-cache.sh
./scripts/refresh-ti-cache.sh --if-stale 24
COMPASS_TI_PROVIDER=github-stars-cached ./scripts/query-technology-intelligence.sh --query "react forms"

# Batch categorized stars (offline ML from manual labels — M14)
./scripts/categorize-github-stars.sh --source fixtures
COMPASS_TI_PROVIDER=github-stars-categorized ./scripts/query-technology-intelligence.sh --query "react forms"
COMPASS_TI_PROVIDER=huggingface-file ./scripts/query-technology-intelligence.sh --query "sentence embeddings"
COMPASS_TI_PROVIDER=huggingface-hub ./scripts/query-technology-intelligence.sh --query "sentence embeddings"
COMPASS_TI_PROVIDER=package-registry-file ./scripts/query-technology-intelligence.sh --query "schema validation"
COMPASS_TI_PROVIDER=package-registry ./scripts/query-technology-intelligence.sh --query "schema validation"
```

## Plan rendering

The plan writer (`orchestrator/plan_writer/render.py`) always renders a
**Technology Intelligence Candidates** section with this banner:

```markdown
> **NOT APPROVED FOR EXECUTION** — discovery signals only.
```

| Provider result | Rendered content |
|---|---|
| Empty (stub) | *No external candidates queried (Technology Intelligence provider: stub).* |
| Non-empty (file) | Markdown table: ID, discovery signal, lifecycle stage |

Candidates appear **only** in this section — never in Skill ranking, task
manifests, or install targets.

## Current status (M7 / v1.11.0)

| Component | Status |
|---|---|
| `TechnologyIntelligenceProvider` protocol | Shipped |
| `StubTechnologyIntelligenceProvider` | Shipped — returns `[]` (CI default) |
| `FileTechnologyIntelligenceProvider` | Shipped — redacted Stars-shaped fixtures |
| `GithubStarsTechnologyIntelligenceProvider` | Shipped — live starred repos via `gh` (opt-in) |
| `CachedGithubStarsTechnologyIntelligenceProvider` | Shipped — offline cache via `github-stars-cached` (M8) |
| `GithubStarsCategorizedTechnologyIntelligenceProvider` | Shipped — batch ML categories via `github-stars-categorized` (M14) |
| `refresh-ti-cache.sh` | Shipped — explicit cache refresh CLI (M8); `--if-stale` (M10) |
| `HuggingFaceFileTechnologyIntelligenceProvider` | Shipped — offline HF model cards via `huggingface-file` (M10) |
| `HuggingFaceHubLiveTechnologyIntelligenceProvider` | Shipped — live Hub via `huggingface-hub` (M16; Captain local) |
| `PackageRegistryFileTechnologyIntelligenceProvider` | Shipped — offline npm/PyPI via `package-registry-file` (M11) |
| `PackageRegistryLiveTechnologyIntelligenceProvider` | Shipped — live npm+PyPI via `package-registry` (M12; Captain local) |
| Fixture `EmbeddingProvider` + dense index | Shipped — `COMPASS_EMBEDDING_PROVIDER=fixture` (M11); TF-IDF fallback |
| OpenAI-compatible `EmbeddingProvider` | Shipped — `openai-compatible` + `COMPASS_EMBEDDING_*` (M12; mocked in CI) |
| `CandidateCapability` + schema | Shipped |
| Pre-render validation | Shipped |
| `query-technology-intelligence.sh` | Shipped — explicit Captain TI queries |
| Candidate promotion `DISCOVERED → SANDBOX_TESTED` | Shipped (`candidate-promotion` Skill) |
| Candidate promotion `APPROVED → PROVEN_SKILL` | Shipped (`skill-lifecycle` Skill; `--captain-approved`) |
| AVAILABLE_SKILL install proposals | Shipped — staging only; never auto-install |
| Captain-approved Skill sidecar PR path | Shipped (draft under staging; never auto-merge) |
| Batch GitHub Star Categorization ML pipeline | **Deferred** — M7 is live query adapter only |
| Auto-install / execute external repos | **Prohibited** |

## Promotion path

```text
DISCOVERED → ANALYZED → SECURITY_REVIEWED → SANDBOX_TESTED
  → APPROVED → AVAILABLE_SKILL → PROVEN_SKILL
```

Pre-sandbox: Skill `candidate-promotion`. Post-sandbox: Skill `skill-lifecycle`
with `--captain-approved`. `AVAILABLE_SKILL` writes a proposal under
`.agent/capabilities/candidates/available-proposals/` — live install still
requires a Captain-reviewed PR. `PROVEN_SKILL` requires ≥2 successful Experiences
(default; `COMPASS_PROVEN_SUCCESS_THRESHOLD`). Never auto-merge or set
`approved_for_execution: true`.

Scripts:

- `./scripts/promote-candidate.sh`
- `./scripts/train-skill-from-experience.sh` (product Experience → control draft)

## Implementing a future live provider

1. Add a class implementing `TechnologyIntelligenceProvider` (e.g. `github_stars.py`).
2. Map external records to `CandidateCapability` — `approved_for_execution` always
   `false` via `to_dict()`.
3. Unit-test with golden fixtures; never call live APIs in CI.
4. Extend `select_ti_provider()` behind an explicit env value (not default).
5. Document provenance, rate limits, and secret handling here.
6. Extend `tests/evals/run.sh` isolation sensors if behavior changes.

**Do not:**

- Import code from starred or external repositories at planning time
- Add candidates to the compiled Skill registry without Captain approval
- Grant agent manifests tools/permissions based on TI output alone
- Skip schema validation

## Captain Compass responsibilities

- Display candidates separately from approved Skills
- Never auto-install or execute external repositories
- Require explicit Captain approval before candidate promotion lands
- Keep TI adapters optional; product repos receive this doc via install for policy
  awareness; the Python orchestrator remains control-repo only

## Related artifacts

- Schema: `orchestrator/schemas/candidate-capability.schema.json`
- File fixtures: `orchestrator/providers/technology_intelligence/fixtures/`
- Stub/file tests: `tests/orchestrator/test_schemas.py`,
  `tests/orchestrator/test_file_ti_and_promotion.py`
- Eval isolation: `tests/evals/run.sh` (stub + file TI sensors)
- Skills: `capability-planning`, `candidate-promotion`, `experience-skill-training`,
  `technology-intelligence-live`
