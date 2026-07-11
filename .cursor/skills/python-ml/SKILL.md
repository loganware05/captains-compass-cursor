---
name: python-ml
description: Implements Python services, data processing, model training/eval, and reproducible ML experiment workflows
---

# Python and Machine Learning

## Use this Skill when

Working on Python services, data pipelines, model training/evaluation, inference, experiment logging, dataset contracts, or ML reproducibility requirements.

## Inputs

- Approved IMPLEMENTATION_PLAN.md
- Existing Python package layout, dependency manager (pip/poetry/uv), and test runner
- Dataset and experiment constraints from PROJECT_CONTEXT.md

## Procedure

1. Match existing project packaging and lint/test tooling.
2. Keep training, evaluation, and inference entrypoints explicit and documented.
3. Pin or lock dependencies according to project convention; record versions in evidence when relevant.
4. Separate raw data, processed data, and model artifacts; do not commit large datasets or weights by default.
5. Define dataset contracts (schema, split, labels) before changing training code.
6. Log experiment configuration (seed, hyperparams, data revision) for reproducibility.
7. Add unit tests for transforms/metrics and smoke tests for training/inference when feasible.
8. Record commands, metrics, and artifact locations under `.agent/evidence/`.

## Prohibited actions

- Do not commit secrets, raw PII datasets, or production model credentials
- Do not silently change evaluation metrics or baselines to force a “win”
- Do not run expensive cloud training without Captain approval and a budget
