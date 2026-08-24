---
name: external-knowledge-ingest
description: Ingests Captain-exported Notion and NotebookLM files into Knowledge Steward (explicit CLI)
---

# External Knowledge Ingest

## Use this Skill when

The Captain has **exported** Notion pages or NotebookLM learning notes as local
files and wants them durable in `.agent/knowledge/` for planning readback.

This Skill does **not** call live Notion MCP or NotebookLM APIs. For MCP
coordination during planning, use Skill `notion-integration`.

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
