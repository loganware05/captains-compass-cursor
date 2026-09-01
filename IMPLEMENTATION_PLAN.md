# Implementation Plan — Post-Foundation Backlog (M13–M18)

- Status: COMPLETE — M16 / v1.20.0 release prep
- Plan ID: post-foundation-backlog
- Issue: #98

| Field | Value |
|---|---|
| **Plan ID** | `post-foundation-backlog` |
| **Status** | **COMPLETE** — M16 / v1.20.0 release prep; M17 next |
| **Baseline** | v1.16.0 (`9d50de8`) |
| **Issue** | [#86](https://github.com/loganware05/captains-compass-cursor/issues/86) (M13 closed) |
| **Feature PR** | [#87](https://github.com/loganware05/captains-compass-cursor/pull/87) (merged @ `40c84fc`) |
| **Target release** | **v1.17.0** |
| **Branch** | `chore/86-release-v1.17.0` |
| **Rollback** | `rollback/pre-m13-hosted-pgvector` |
| **Captain approval** | 2026-08-30 |

## Captain decisions (locked)

| # | Topic | Decision |
|---|---|---|
| 1 | Hosted vector DB | **Neon/pgvector** (see cost analysis below) |
| 2 | Index layout | Single shared index with **namespaces** per repo |
| 3 | M14 labels | **Learn from existing manual labels** |
| 4 | M15 Notion | **Allowlist of page IDs** |
| 5 | M17 autonomy | **Context selection first**, then light decomposition |
| 6 | M18 smokes | **Required** for release closeout |

## Cost analysis — Pinecone vs Neon/pgvector

Estimated Compass workload: ~500–2,000 knowledge items, \<10k vector queries/month,
embedding dims 32 (fixture) or 1536 (OpenAI-compatible).

| Scenario | Pinecone | Neon/pgvector |
|---|---|---|
| Today (free tier) | **$0** — Starter: 2 GB, 1M RU, 2M WU | **$0** — Free: 0.5 GB, 100 CU-hrs |
| 10× queries (~50k/mo) | **$0** — ~12.5k RU at 0.25 RU/query min | **$0–3** — likely still free or Launch PAYG |
| Exceed Pinecone Starter | **$50/mo minimum** (Standard) + usage | **~$5–15/mo** PAYG (no floor) |
| Ops complexity | Lower (managed vector API) | Medium (Postgres + pgvector DDL) |
| Namespace isolation | Native | `namespace` column (Captain choice) |
| Existing MCP | Pinecone MCP | Neon MCP |

**Choice: Neon/pgvector** — same $0 cost today, lower cost ceiling beyond free tier,
namespaces via column, aligns with existing `postgres-prisma` Skill and Neon MCP.

Pinecone remains a viable second adapter if requirements change.

---

## Roadmap

| Milestone | Version | Theme | Status |
|---|---|---|---|
| **M13** | v1.17.0 | Hosted pgvector/Neon adapter | **Complete** (#87) |
| **M14** | v1.18.0 | Batch GitHub Star categorization ML | **Complete** (#91) |
| **M15** | v1.19.0 | Live Notion MCP ingest (page allowlist) | **Complete** (#95) |
| **M16** | v1.20.0 | Live Hugging Face Hub TI | **Complete** (#99) |
| **M17** | v1.21.0 | Stage 3: context selection → light decomposition | **Next** |
| **M18** | v1.22.0 | Required interactive sandbox release smokes | Planned |

---

# M13 — Hosted pgvector/Neon (v1.17.0) — COMPLETE

## Objective

Hosted vector search via Neon/pgvector with namespace isolation, mock backend for CI,
explicit sync CLI, TF-IDF + file dense fallback preserved.

## Implementation checklist

- [x] `orchestrator/knowledge/adapters/pgvector.py` — mock + live backends
- [x] Query integration (hosted → dense file → TF-IDF)
- [x] `scripts/sync-knowledge-vector-db.sh`, `scripts/init-pgvector-schema.sh`
- [x] Skill `hosted-vector-db` + docs + ADR-029
- [x] Unit tests (`test_m13_pgvector_hosted.py`)
- [x] Full `./tests/run.sh` validation evidence
- [x] Feature PR [#87](https://github.com/loganware05/captains-compass-cursor/pull/87) merged
- [x] Release tag [v1.17.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.17.0)
- [x] Sandbox refresh [sandbox#34](https://github.com/loganware05/captain-compass-sandbox/pull/34)
- [x] Closeout + issue #86 closed

## Env vars

| Variable | Purpose |
|---|---|
| `COMPASS_VECTOR_PROVIDER` | `file` (default), `mock`, `pgvector` |
| `COMPASS_VECTOR_DATABASE_URL` | Neon Postgres DSN (live only) |
| `COMPASS_VECTOR_NAMESPACE` | Per-repo namespace (default: repo dir name) |
| `COMPASS_VECTOR_DIMENSIONS` | Schema bootstrap dimensions (default 32) |

---

# M14 — Batch GitHub Star Categorization ML (v1.18.0) — COMPLETE

Offline batch pipeline; labels learned from **existing manual categories**; new
`github-stars-categorized` TI provider; fixtures in CI.

## Checklist

- [x] Manual label fixtures from curated Stars fixtures
- [x] Naive Bayes batch pipeline + `categorize-github-stars.sh`
- [x] `github-stars-categorized` TI provider
- [x] ADR-030, docs, Skill extension, tests
- [x] Feature PR [#91](https://github.com/loganware05/captains-compass-cursor/pull/91) merged
- [x] Release tag [v1.18.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.18.0)
- [x] Sandbox refresh [sandbox#35](https://github.com/loganware05/captain-compass-sandbox/pull/35)
- [x] Closeout + issue #89 closed

---

# M15 — Live Notion MCP Knowledge Ingest (v1.19.0) — COMPLETE

Explicit CLI; **allowlist of Notion page IDs**; provenance `export_mode: mcp_live`;
file-export path unchanged.

## Checklist

- [x] Allowlist loader + page ID normalization
- [x] `ingest-notion-live.sh` (cache / fixtures / live payload sources)
- [x] ADR-031, docs, Skill extensions, tests
- [x] Feature PR [#95](https://github.com/loganware05/captains-compass-cursor/pull/95) merged
- [x] Release tag [v1.19.0](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.19.0)
- [x] Sandbox refresh [sandbox#36](https://github.com/loganware05/captain-compass-sandbox/pull/36)
- [x] Closeout + issue #94 closed

---

# M16 — Live Hugging Face Hub TI (v1.20.0) — COMPLETE

Live Hub provider mirroring M12 package-registry pattern; mocked HTTP in CI.

## Checklist

- [x] `HuggingFaceHubLiveTechnologyIntelligenceProvider` + Hub models API
- [x] `COMPASS_TI_PROVIDER=huggingface-hub` selection + optional `COMPASS_HF_HUB_TOKEN`
- [x] ADR-032, docs, Skill extension, tests
- [x] Feature PR [#99](https://github.com/loganware05/captains-compass-cursor/pull/99) merged
- [ ] Release tag v1.20.0 + sandbox refresh + closeout

---

# M17 — Deeper Stage 3 Bounded Autonomy (v1.21.0)

Priority order per Captain:

1. **Context selection tuning** proposals (which knowledge/TI slices appear in plans)
2. **Light decomposition hints** (finer matcher sub-capability weights)

All proposal-only until `captain_approved: true`; budget-enforced.

---

# M18 — Interactive Sandbox Release Smokes (v1.22.0)

Interactive smokes **required** for release closeout. Expand behavioral checklist,
evidence templates, release-checklist integration; clear all pending sandbox rows.

---

## Approval record

| Captain | Decision | Date |
|---|---|---|
| loganware | **APPROVED** — post-foundation backlog + Captain decisions above | 2026-08-30 |
