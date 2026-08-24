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
  `runs`, `decisions`)
- Search query for readback

## Procedure

1. **Ingest** (explicit CLI only — never auto-run on workstream close):

   ```bash
   ./scripts/ingest-knowledge.sh --from-store experience,evaluations,decisions
   ./scripts/ingest-knowledge.sh --paths tests/fixtures/experience/contact-counter.json
   ```

   `decisions` auto-ingests **ADR headings** from `DECISIONS.md`.

2. **Query** for planning context (read-only):

   ```bash
   ./scripts/query-knowledge.sh --query "evaluator routing" --kind decision
   ```

3. Review matches under `.agent/knowledge/items/` with provenance.
4. Optionally propose a reusable procedure (staging + Captain PR only):

   ```bash
   ./scripts/propose-procedure-from-knowledge.sh \
     --item-ids know-adr-020 \
     --title "Bounded weight apply playbook"
   ```

5. Use the **Knowledge Context** section in capability plans as informational
   input only — it does not alter Skill rankings or matcher weights.

## Output

- Knowledge items under `.agent/knowledge/items/`
- Rebuilt `.agent/knowledge/index.json`
- Ingest audit under `.agent/knowledge/ingest-log/`
- Optional procedure staging under `.agent/knowledge/procedures/staging/`

## Prohibited actions

- Auto-ingest on workstream close without explicit CLI
- Silent install of procedures into `.cursor/skills/` or rules
- Mutating matcher weights from query results
- Ingesting secret paths (`.env`, credentials)
