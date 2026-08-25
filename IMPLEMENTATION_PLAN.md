# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: m10-external-knowledge-ti
- Issue: [#74](https://github.com/loganware05/captains-compass-cursor/issues/74) — M10: External knowledge ingest + Hugging Face file TI (v1.14.0)
- Branch: `feature/74-m10-external-knowledge-ti` (merged #75)
- Target release: **v1.14.0** (released 2026-08-24)
- Created: 2026-08-24
- Last updated: 2026-08-24
- Approved by: Captain
- Approval date: 2026-08-24
- Approved revision: v1.14.0; both knowledge+HF TI; file export only; fetched_at + --if-stale; dedicated external-knowledge-ingest Skill
- Rollback checkpoint: `rollback/pre-m10-external-knowledge-ti` @ `bc5f8a7`
- Feature PR: [#75](https://github.com/loganware05/captains-compass-cursor/pull/75) (merged @ `f99dda5`)
- Source documents:
  - Notion: [Captain Compass Multi-Agent Orchestration OS — Architecture & Production Plan](https://app.notion.com/p/3c1e6a901c4381c4bb5fdc91dc8b4d71)
  - Prior plans: M1–M9 COMPLETE (v1.5.0–v1.13.0)
  - Baseline: **v1.13.0** (`bc5f8a7`)
- Machine artifacts: `.agent/plans/m10-external-knowledge-ti/`

## Request

Milestone 10: file-export Notion/NotebookLM knowledge ingest + Hugging Face file TI
+ TI cache `fetched_at` / `--if-stale`.

## Acceptance Criteria

- [x] Notion + NotebookLM file ingest → `kind: knowledge` (explicit CLI)
- [x] `COMPASS_TI_PROVIDER=huggingface-file` with golden fixtures
- [x] TI cache `fetched_at` + `refresh-ti-cache.sh --if-stale <hours>`
- [x] Skill `external-knowledge-ingest`; extend knowledge-steward + technology-intelligence-live; ADR-026
- [x] Doctor / tests / evals pass (36 Skills)
- [ ] Control-repo only; sandbox refresh after release (closeout PR)

## Open Questions (Captain — resolved 2026-08-24)

1. **v1.14.0**
2. **Both** knowledge ingest and HF file TI
3. **File export only**
4. **`fetched_at` and `refresh-ti-cache.sh --if-stale`**
5. Dedicated **`external-knowledge-ingest`** Skill

## Approval Record

- **Approved by:** Captain
- **Approval date:** 2026-08-24
- **Approved revision:** v1.14.0; both; file export; fetched_at + --if-stale; external-knowledge-ingest Skill
- **Issue:** #74
- **Branch:** feature/74-m10-external-knowledge-ti
- **Rollback:** rollback/pre-m10-external-knowledge-ti @ bc5f8a7
- **Feature PR:** #75 (merged)
- **Release:** v1.14.0 (2026-08-24)
