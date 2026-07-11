---
name: notion-integration
description: Reads Notion requirements/research and writes release summaries when MCP is available; never stores approval-critical state only in Notion
---

# Notion Integration (MCP Stage 4)

## Use this Skill when

Reading product requirements or research from Notion, or writing release summaries after a completed change.

## Prerequisites

- Notion MCP enabled in Cursor with least-privilege access
- Repository remains authoritative for plans, decisions, and approvals

## Allowed Stage 4 capabilities

- Reading requirements
- Reading project research
- Writing release summaries

## Procedure

1. Confirm Notion access via MCP.
2. Pull requirements/research into the planning phase; cite page links in IMPLEMENTATION_PLAN.md.
3. After validation, optionally write a short release summary page/section.
4. Mirror any durable decisions into DECISIONS.md in the repository.
5. If Notion is unavailable, continue with repo docs only and report the gap.

## Prohibited actions

- Do not store implementation-critical approvals only in Notion
- Do not replace IMPLEMENTATION_PLAN.md / DECISIONS.md with Notion-only records
- Do not grant write access to pages outside the agreed project space
