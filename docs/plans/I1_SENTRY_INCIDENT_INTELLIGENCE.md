# Queued Plan — I1 Sentry Production Incident Intelligence

- Status: **QUEUED** (after `conversation-trajectory-ingest` / v1.77.0)

## Metadata

| Field | Value |
|---|---|
| Status | **QUEUED** |
| Plan ID | `i1-sentry-incident-intelligence` |
| Priority | Next after conversation trajectory ingest |
| Follow-on | I2 T3 execution adapter (queued behind I1) |
| Baseline intent | Read-only Sentry adapter → evidence packets for Overseer / Code Reviewer |
| Source | ChatGPT integration roadmap (Captain queued 2026-11-06) |

## Intent (not yet an active IMPLEMENTATION_PLAN)

Ship a gated, read-only Sentry incident adapter that normalizes issues into
NorthStar evidence without granting repair authority. Full
`IMPLEMENTATION_PLAN.md` to be drafted and presented for Captain approval when
this queue item becomes active.

## Non-goals (preview)

- Auto-fix production from Sentry events
- Write scopes to Sentry
- I2–I5 in the same sprint

## Activation

When conversation-trajectory-ingest merges (or Captain redirects), First Mate
shall draft full `IMPLEMENTATION_PLAN.md` for I1 and pause at AWAITING APPROVAL
unless Captain pre-approves a fuller I1 plan in-thread.
