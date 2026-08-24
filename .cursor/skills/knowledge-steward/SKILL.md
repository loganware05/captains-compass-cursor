---
name: knowledge-steward
description: Ingests and queries the project knowledge store for planning context (explicit CLI)
---

# Knowledge Steward

## Use this Skill when

The Captain or First Mate needs durable project knowledge surfaced during
planning — Experiences, evaluations, routing artifacts, execution runs, and
ADR headings from `DECISIONS.md`.

## Inputs

- Explicit file paths or store roots (`experience`, `evaluations`, `routing`,
  `runs`, `decisions`, `procedures`, `notion`, `notebooklm`)
- Search query for readback

## Procedure

1. **Ingest** (explicit CLI only — never auto-run on workstream close):

   ```bash
   ./scripts/ingest-knowledge.sh --from-store experience,evaluations,decisions
   ./scripts/ingest-knowledge.sh --paths tests/fixtures/experience/contact-counter.json
   ```

   `decisions` auto-ingests **ADR headings** from `DECISIONS.md`.

   For Captain-exported Notion / NotebookLM files, use Skill
   `external-knowledge-ingest` or:

   ```bash
   ./scripts/ingest-knowledge.sh --from-store notion,notebooklm
   ```

2. **Query** for planning context (read-only):

   ```bash
   ./scripts/query-knowledge.sh --query "evaluator routing" --kind decision
   ./scripts/query-knowledge.sh --query "matcher tuning" --kind performance --mode hybrid
   ./scripts/ingest-knowledge.sh --from-store runs,experience
   ```

   Execution runs ingest as `kind: performance` with `performance_metrics`
   (outcome, retries, skills, agents, models). Re-ingest overwrites existing
   `know-run-*` / `know-exp-*` items idempotently.

   When `.agent/knowledge/vector-index.json` exists, capability plans use **hybrid**
   search for Knowledge Context by default. Override with
   `COMPASS_KNOWLEDGE_SEARCH_MODE=keyword|vector|hybrid`.

3. **Rebuild vector index** (explicit CLI only):

   ```bash
   ./scripts/rebuild-knowledge-vector-index.sh
   ./scripts/ingest-knowledge.sh --from-store decisions --rebuild-vector
   ```

4. Review matches under `.agent/knowledge/items/` with provenance.
5. Optionally propose a reusable procedure (staging + Captain PR only):

   ```bash
   ./scripts/propose-procedure-from-knowledge.sh \
     --item-ids know-adr-020 \
     --title "Bounded weight apply playbook"
   ```

6. Use the **Knowledge Context** section in capability plans as informational
   input only — it does not alter Skill rankings or matcher weights.
7. Review **Performance Context** in capability plans (always rendered; empty
   when no `kind: performance` items match).
8. For procedure playbooks, use Skill `procedure-playbooks` or
   `--from-store procedures` after staging/approved playbooks exist.

## Output

- Knowledge items under `.agent/knowledge/items/`
- Rebuilt `.agent/knowledge/index.json`
- Optional `.agent/knowledge/vector-index.json` after explicit rebuild
- Ingest audit under `.agent/knowledge/ingest-log/`
- Optional procedure staging under `.agent/knowledge/procedures/staging/`

## Prohibited actions

- Auto-ingest on workstream close without explicit CLI
- Silent install of procedures into `.cursor/skills/` or rules
- Mutating matcher weights from query results
- Ingesting secret paths (`.env`, credentials)
