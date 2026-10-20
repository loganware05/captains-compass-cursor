> **IN PROGRESS** — [#222](https://github.com/loganware05/captains-compass-cursor/issues/222).
> Plan ID `e2e-cognitive-core-evaluation`.
> Branch: `cursor/222-e2e-cognitive-core-evaluation-3ec1`.
> Rollback: `rollback/pre-e2e-cognitive-core-evaluation` @ `bb1b5b9`.
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md`.

# E2E Cognitive Core Evaluation (C1–C7)

Prerequisite: C1–C7 shipped (v1.66.0 / #219) + post-C7 closeout (v1.66.1 / #221)
+ plan docs (#223).

## One-line summary

Hermetic C1–C7 evaluation harness with schema-validated report and measured
baselines — no new authority.

## Operator surface

```bash
./scripts/run-cognitive-core-e2e.sh --repo-root . --enable-gates --mode hermetic
./scripts/northstar cognitive e2e --repo . --enable-gates
```

## Non-goals

Persistent oversight automation; Specialized Model fine-tuning / weight
promotion; HTTP `/v1/*` server; live REA or live embeddings required for CI.
