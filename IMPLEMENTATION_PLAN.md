# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m12-live-embeddings-registry
- Issue: [#82](https://github.com/loganware05/captains-compass-cursor/issues/82) — M12: Live OpenAI-compatible embeddings + package-registry TI + soft-hook skips (v1.16.0)
- Branch: `feature/82-m12-live-embeddings-registry` (merged #83)
- Target release: **v1.16.0** (released 2026-08-24)
- Created: 2026-08-24
- Last updated: 2026-08-24 (closeout: sandbox #33)
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: v1.16.0; embeddings+live package TI; COMPASS_EMBEDDING_*; npm+PyPI; extend existing Skills; include soft-hook compass-skip.env
- Rollback checkpoint: `rollback/pre-m12-live-embeddings-registry` @ `1f9d948`
- Feature PR: [#83](https://github.com/loganware05/captains-compass-cursor/pull/83) (merged @ `fbb3aee`)
- Source documents:
  - Notion architecture plan; M11 ADR-027 deferrals
  - Baseline: **v1.15.0** (`1f9d948`)
- Machine artifacts: `.agent/plans/m12-live-embeddings-registry/`

## Request

Milestone 12: live OpenAI-compatible embeddings + live npm/PyPI TI + soft-hook skip-env.

## Acceptance Criteria

- [x] `OpenAICompatibleEmbeddingProvider` implementing `EmbeddingProvider`
- [x] Env contract `COMPASS_EMBEDDING_API_KEY` / `BASE_URL` / `MODEL`; secrets never logged
- [x] Fail closed without key/URL; unknown providers fall back to TF-IDF
- [x] CI tests use mocked HTTP only
- [x] Dense rebuild + query; TF-IDF fallback on live failure
- [x] Live package-registry TI (npm + PyPI); Skill updates
- [x] Soft-hook `.agent/compass-skip.env` inheritance
- [x] ADR-028; extend existing Skills only
- [x] Doctor / install / tests / evals pass
- [x] Control-repo only; sandbox refresh after release ([sandbox#33](https://github.com/loganware05/captain-compass-sandbox/pull/33))

## Open Questions (Captain — resolved 2026-08-24)

1. **v1.16.0**
2. **Both** embeddings and live package-registry TI
3. **`COMPASS_EMBEDDING_*`**
4. **Both** npm and PyPI
5. **Extend** existing Skills only
6. **Include** soft-hook `compass-skip.env`

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-24
- **Approved revision:** as above
- **Issue:** #82
- **Branch:** feature/82-m12-live-embeddings-registry
- **Rollback:** rollback/pre-m12-live-embeddings-registry @ 1f9d948
- **Feature PR:** #83 (merged)
- **Release:** v1.16.0 (2026-08-24)
