---
name: procedure-playbooks
description: Ingests and surfaces procedure playbooks as knowledge for planning (explicit CLI)
---

# Procedure Playbooks

## Use this Skill when

The Captain or First Mate needs **reusable procedure playbooks** surfaced during
planning — validated sequences from staging or approved procedure roots.

## Prerequisites

- Playbooks under `.agent/knowledge/procedures/staging/` or `.../approved/`
- Optional prior step: `propose-procedure-from-knowledge.sh` (staging only)

## Procedure

1. **Propose** (optional — creates staging draft, does not ingest):

   ```bash
   ./scripts/propose-procedure-from-knowledge.sh \
     --item-ids know-adr-020 \
     --title "Bounded weight apply playbook"
   ```

2. **Ingest** procedure playbooks (explicit CLI only):

   ```bash
   ./scripts/ingest-knowledge.sh --from-store procedures
   ```

   Ingests `playbook.md` from **staging** and **approved** roots. Re-ingest
   overwrites existing `know-proc-*` items idempotently.

3. **Query** for readback:

   ```bash
   ./scripts/query-knowledge.sh --query "bounded autonomy apply" --kind procedure
   ```

4. Review **Procedure Context** in capability plans (always rendered; empty when none).

5. Land approved playbooks via Captain-reviewed PR — never auto-install into Skills.

## Output

- Knowledge items `kind: procedure` under `.agent/knowledge/items/`
- Plan section **Procedure Context** (informational only)

## Prohibited actions

- Auto-ingest on procedure proposal write
- Silent install of playbooks into `.cursor/skills/` or rules
- Mutating matcher weights from procedure readback
