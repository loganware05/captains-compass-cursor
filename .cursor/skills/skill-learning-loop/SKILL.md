---
name: skill-learning-loop
description: Runs categorized Stars skill learning loop — drafts new Skills and proposes improvements to similar existing Skills (Captain-gated live install)
---

# Skill Learning Loop

## Use this Skill when

The Captain wants to **learn from categorized GitHub Stars** inside the disposable
sandbox (or control-repo fixtures) to:

1. Draft **new** Skills from high-signal categorized candidates
2. **Improve existing** Compass Skills when candidate processes are similar
3. Capture sandbox-test evidence through `SANDBOX_TESTED`
4. Stop for **Captain approval** before any live `.cursor/skills/` install

## Prerequisites

- Compass ≥ 1.23.0 (M19)
- Explicit CLI only — never from hooks or CI defaults
- Understanding: staging + evidence ≠ auto-install

## Inputs

- Objective text (for ranking)
- Source: `fixtures` (CI default), `ti-cache`, or `live` (Captain-local `gh`)
- Optional category filter and similarity threshold

## Procedure

### A. Run the learning loop (staging + evidence)

```bash
./scripts/run-skill-learning-loop.sh \
  --source fixtures \
  --objective "accessible react forms"
```

Captain-local cache / live Stars:

```bash
./scripts/refresh-ti-cache.sh
./scripts/run-skill-learning-loop.sh --source ti-cache --objective "schema validation"
# or:
./scripts/run-skill-learning-loop.sh --source live --objective "schema validation"
```

Artifacts:

- Staging candidates: `.agent/capabilities/candidates/staging/`
- Unified drafts: `.agent/capabilities/candidates/skill-drafts/<slug>/`
- Improvement proposals (when similar): `.agent/capabilities/candidates/skill-improvement-proposals/<existing-slug>/`
- Harness evidence: `.agent/evidence/candidate-sandbox-test/`
- Learning-run report: `.agent/learning-runs/`

### B. New Skill drafts

When no existing Skill is similar enough, the loop emits `SKILL.md` +
`capability.yaml` under `skill-drafts/`. Review with the Captain, then promote
via Skills `candidate-promotion` / `skill-lifecycle` with `--captain-approved`
before copying into `.cursor/skills/`.

### C. Improve existing Skills when processes are similar

When Jaccard/overlap similarity between the candidate and a live Skill exceeds the
threshold (default `0.28`), the loop writes a **skill-improvement-proposal**
targeting that Skill. Proposals never mutate live `SKILL.md`. Meta and
safety-critical Skills are excluded from automatic targeting.

1. Review the proposal JSON (suggested procedure lessons + provenance).
2. Captain decides whether to fold lessons into the existing Skill via PR.
3. Do **not** auto-apply proposals.

### D. Captain gate for live promotion

```bash
./scripts/promote-candidate.sh --candidate <staging.json> \
  --stage AVAILABLE_SKILL \
  --evidence .agent/evidence/candidate-sandbox-test/<id>/sandbox-test.json \
  --captain-approved \
  --skill-slug <slug>
```

Then open a Captain-reviewed PR to install. Never set `approved_for_execution: true`.

## Output

- Learning-run JSON report
- Staging candidates at `SANDBOX_TESTED`
- New Skill drafts and/or improvement proposals
- Evidence suitable for promotion gates

## Prohibited actions

- Auto-installing into `.cursor/skills/`
- Auto-applying improvement proposals to live Skills
- Setting `approved_for_execution: true`
- Cloning or executing starred/external repositories
- Running the loop from hooks, workstream close, or CI defaults
- Advancing past `SANDBOX_TESTED` without `--captain-approved`
