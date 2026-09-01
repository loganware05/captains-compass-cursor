# Interactive sandbox release smoke report

- **Version:** X.Y.Z
- **Date:**
- **Sandbox path:**
- **Agent / Captain:**

## Checklist results

| # | Behavior | Pass | Notes |
|---|---|---|---|
| 1 | Approval gate | | |
| 2 | No implement on DRAFT | | |
| 3 | No weaken tests | | |
| 4 | Evidence capture | | |
| 5 | Budget stop | | |
| 6 | Phase commands | | |
| 7 | Capability-aware `/plan-feature` | | |
| 8 | Post-foundation smokes (M13–M17) | | |

## Post-foundation fixture spot-checks (item 8)

- [ ] Knowledge ingest (`ingest-knowledge.sh --from-store procedures`)
- [ ] Mock pgvector query (`query-knowledge.sh --mode vector` with `COMPASS_VECTOR_PROVIDER=mock`)
- [ ] Stars categorization fixtures (`categorize-github-stars.sh --source fixtures`)
- [ ] Notion live fixtures (`ingest-notion-live.sh --source fixtures`)
- [ ] HF file TI (`query-technology-intelligence.sh --provider huggingface-file`)
- [ ] Context selection propose (`propose-context-selection.sh`)
