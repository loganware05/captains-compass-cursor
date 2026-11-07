# Implementation Plan — Conversation Trajectory Ingest (ChatGPT / Obsidian → NorthStar)

- Status: **COMPLETE**

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `conversation-trajectory-ingest` |
| Issue | [#247](https://github.com/loganware05/captains-compass-cursor/issues/247) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.76.0** @ `c46c161` |
| Branch | `feature/247-conversation-trajectory-ingest` |
| Rollback | `rollback/pre-conversation-trajectory-ingest` @ `c46c161` |
| Proposed release | **v1.77.0** |
| Captain | Logan Ware |
| Created | 2026-11-06 |
| Queued next | I1 Sentry (`docs/plans/I1_SENTRY_INCIDENT_INTELLIGENCE.md`), then I2 T3 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Logan Ware (Captain) |
| Approval date | 2026-11-06 |
| Notes | Standing order: approval ⇒ implement → validate → commit → open PR. Queue I1 Sentry then I2 T3. FF local main completed. |

## Request

Ship gated conversation trajectory ingest for Obsidian AI Exporter / ChatGPT
markdown so NorthStar can store `user_prompt` + `model_or_source` +
`assistant_suggestion` as external evidence without granting authority.

## Acceptance Criteria

- [x] Fail-closed without `COMPASS_CONVERSATION_INGEST_ENABLED=1`
- [x] Parses Obsidian AI Exporter ChatGPT markdown into ≥1 trajectory per Q/A turn
- [x] Schema validation; authority flags always false
- [x] Ingest writes store + ingest-log; Knowledge Steward `know-conv-*` items
- [x] Does not mutate `.cursor/`, policies, routing, or canonical memory docs
- [x] Fixtures + unit tests; doctor updated
- [x] Docs: handbook blurb, `docs/integrations/conversation-ingest.md`, CHANGELOG, ADR
- [x] Evidence under `.agent/evidence/conversation-trajectory-ingest/`
- [x] Implementation on FF'd `origin/main` v1.76.0 baseline
- [ ] PR opened (standing order)

## Non-Goals

- Live ChatGPT scraping; auto-promotion; Level 3; I1–I5 implementation in this PR
- C7 `source: conversations` enum extension (deferred; knowledge + exemplar drafts only)

## Rollback

1. Disable `COMPASS_CONVERSATION_INGEST_ENABLED`
2. Revert merge / checkout `rollback/pre-conversation-trajectory-ingest`
