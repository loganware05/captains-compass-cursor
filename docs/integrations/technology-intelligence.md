# Technology Intelligence integration (adapter boundary)

Captain Compass consumes **normalized candidate capabilities** from external
Technology Intelligence sources. The GitHub Star Categorization project and other
feeds connect through a provider adapter — not direct repository coupling.

## Provider contract

Implement `TechnologyIntelligenceProvider.discover_candidates(objective, context)`
in `orchestrator/providers/technology_intelligence/`.

Candidates must:

- Use `kind: candidate` and `approved_for_execution: false`
- Stay at lifecycle stages `DISCOVERED` or `ANALYZED` until promoted through review
- Appear only in the **Technology Intelligence Candidates** plan section

## Current status (M1)

- Stub provider ships with Captain Compass (returns no candidates)
- Plan writer renders: *No external candidates queried (provider: stub)*

## Promotion path (future)

```text
DISCOVERED → ANALYZED → SECURITY_REVIEWED → SANDBOX_TESTED → APPROVED → AVAILABLE_SKILL → PROVEN_SKILL
```

A GitHub star or external repo is a **discovery signal**, not permission to execute.

## Captain Compass responsibilities

- Display candidates separately from approved Skills
- Never auto-install or execute starred repositories
- Require Captain approval before candidate promotion
