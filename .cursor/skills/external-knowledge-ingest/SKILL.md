---
name: external-knowledge-ingest
description: Ingests Captain-exported Notion and NotebookLM files into Knowledge Steward (explicit CLI)
---

# External Knowledge Ingest

## Use this Skill when

The Captain has **exported** Notion pages or NotebookLM learning notes as local
files and wants them durable in `.agent/knowledge/` for planning readback.

This Skill does **not** call live Notion MCP or NotebookLM APIs during the
default file-export path. For MCP coordination during planning, use Skill
`notion-integration`. For **allowlist-gated live ingest** after MCP fetch, see
**Live Notion MCP ingest** below.

## Live Notion MCP ingest (M15 — Captain local / explicit CLI)

1. Maintain allowlisted page IDs at `.agent/knowledge/notion-allowlist.txt`.
2. Fetch pages via Notion MCP in Cursor; save markdown to
   `.agent/knowledge/external/notion-live/<page-id>.md` (or build a JSON payload).
3. Ingest explicitly:

   ```bash
   ./scripts/ingest-notion-live.sh --source cache
   # offline/CI:
   ./scripts/ingest-notion-live.sh --source fixtures
   # after MCP session payload export:
   ./scripts/ingest-notion-live.sh --source live --payload mcp-pages.json
   ```

4. Items use provenance `export_mode: mcp_live` (distinct from file exports).

## Inputs

- Markdown exports under `.agent/knowledge/external/notion/` or
  `.agent/knowledge/external/notebooklm/`
- Explicit ingest CLI

## Procedure

1. Export content from Notion / NotebookLM to markdown (Captain local).
2. Place files under the matching store root:

   ```text
   .agent/knowledge/external/notion/<slug>.md
   .agent/knowledge/external/notebooklm/<slug>.md
   ```

3. Ingest (explicit CLI only):

   ```bash
   ./scripts/ingest-knowledge.sh --from-store notion,notebooklm
   ```

4. Query as `kind: knowledge`:

   ```bash
   ./scripts/query-knowledge.sh --query "approval gate" --kind knowledge
   ```

5. Items appear in plan **Knowledge Context** after ingest (informational only).

## Output

- Knowledge items `know-notion-*` / `know-nlm-*` with provenance
  `export_mode: file`

## Prohibited actions

- Live Notion MCP or NotebookLM network pull as part of ingest
- Storing approval-critical state only outside the repository
- Auto-ingest on workstream close
- Mutating matcher weights from external knowledge
