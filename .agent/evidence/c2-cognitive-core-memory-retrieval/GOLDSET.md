# Gold-set report — C2 memory/retrieval

| Field | Value |
|---|---|
| Fixture | `tests/fixtures/brain-goldset/questions.json` |
| Questions | 30 positive + 3 negatives |
| Target | ≥90% evidence-linked on positives |
| Mode | keyword (hermetic) |
| Result | **PASS** (`GoldSetTests`) |

Evidence-linked means the context response has **query-ranked knowledge hits
and/or ADR decision links**. Snapshot/git/version metadata alone does **not**
count. Each positive question also asserts its `expect` citation kinds.
Negatives must remain `evidence_linked: false`.
