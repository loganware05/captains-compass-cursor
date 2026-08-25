# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m11-embeddings-package-ti
- Issue: [#78](https://github.com/loganware05/captains-compass-cursor/issues/78) — M11: Embedding provider protocol + package-registry file TI (v1.15.0)
- Branch: `feature/78-m11-embeddings-package-ti` (merged #79)
- Target release: **v1.15.0** (released 2026-08-24)
- Created: 2026-08-24
- Last updated: 2026-08-24
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: v1.15.0; both embeddings+package TI; fixture+protocol only; TF-IDF always fallback; dedicated Skills embedding-providers + package-registry-ti
- Rollback checkpoint: `rollback/pre-m11-embeddings-package-ti` @ `f9677bb`
- Feature PR: [#79](https://github.com/loganware05/captains-compass-cursor/pull/79) (merged @ `46c3f53`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1–M10 COMPLETE (v1.5.0–v1.14.0)
  - Baseline: **v1.14.0** (`f9677bb`)
- Machine artifacts: `.agent/plans/m11-embeddings-package-ti/`

## Request

Milestone 11: fixture EmbeddingProvider + package-registry file TI; TF-IDF always fallback.

## Acceptance Criteria

- [x] `EmbeddingProvider` protocol + selection helper; default path unchanged (TF-IDF)
- [x] `FixtureEmbeddingProvider` with deterministic offline vectors (no network)
- [x] Dense vector index `.agent/knowledge/embedding-index.json` + rebuild CLI
- [x] Hybrid / vector query prefers dense when present; TF-IDF always fallback
- [x] `PackageRegistryFileTechnologyIntelligenceProvider` + npm/PyPI-shaped mapper
- [x] `COMPASS_TI_PROVIDER=package-registry-file` wired; CI default unchanged (`stub`)
- [x] Skills `embedding-providers` + `package-registry-ti`; ADR-027
- [x] Doctor / install / tests / evals pass
- [ ] Control-repo only; sandbox refresh after release (closeout PR)

## Open Questions (Captain — resolved 2026-08-24)

1. **v1.15.0**
2. **Both** embedding and package-registry TI
3. **Fixture + protocol only** (no OpenAI-compatible HTTP)
4. **TF-IDF always as fallback**
5. Dedicated Skills **`embedding-providers`** + **`package-registry-ti`**

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-24
- **Approved revision:** v1.15.0; both; fixture+protocol; TF-IDF fallback; dedicated Skills
- **Issue:** #78
- **Branch:** feature/78-m11-embeddings-package-ti
- **Rollback:** rollback/pre-m11-embeddings-package-ti @ f9677bb
- **Feature PR:** #79 (merged)
- **Release:** v1.15.0 (2026-08-24)
