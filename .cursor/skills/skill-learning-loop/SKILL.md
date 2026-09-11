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

- Compass ≥ 1.28.0 (M23 gates; M19/M20 loop retained); M24 launcher recommended
- Explicit CLI only — never from hooks or CI defaults
- Understanding: staging + evidence ≠ auto-install
- External repos **must be starred** to enter TI
- Before any Skill draft: **security-review** + **dependency-supply-chain**
  evidence artifacts (fail closed if missing)

## Topology (required)

Learning CLIs live only in the **control** repository. Product / sandbox
checkouts do **not** contain `scripts/run-skill-learning-loop.sh`,
`scripts/refresh-ti-cache.sh`, `scripts/promote-candidate.sh`, or
`scripts/northstar`.

```bash
CONTROL=/path/to/captains-compass-cursor
SANDBOX=/path/to/captain-compass-sandbox
```

Prefer the topology-free launcher (maps `--repo` → `--repo-root`):

```bash
"$CONTROL/scripts/northstar" skills learn --repo "$SANDBOX" ...
```

Equivalent direct script form:

```bash
"$CONTROL/scripts/run-skill-learning-loop.sh" --repo-root "$SANDBOX" ...
```

Never run bare `./scripts/...` from inside the sandbox and expect these tools
to exist there.

## Inputs

- Objective text (for ranking)
- Source: `fixtures` (CI default), `ti-cache`, or `live` (Captain-local `gh`)
- Optional category filter (`frontend-ui`, `design-system`, `backend-library`,
  `devtool`, `ml-data`, `other`) and similarity threshold

## Procedure

### A. Run the learning loop (staging + evidence)

```bash
CONTROL=/path/to/captains-compass-cursor
SANDBOX=/path/to/captain-compass-sandbox

"$CONTROL/scripts/northstar" skills learn \
  --repo "$SANDBOX" \
  --source fixtures \
  --objective "accessible react forms"
```

Equivalent:

```bash
"$CONTROL/scripts/run-skill-learning-loop.sh" \
  --repo-root "$SANDBOX" \
  --source fixtures \
  --objective "accessible react forms"
```

Design-system / craft tokens example (starred fixtures):

```bash
"$CONTROL/scripts/example-design-repo-scorecard.sh"
# or:
"$CONTROL/scripts/northstar" skills learn \
  --repo "$SANDBOX" \
  --source fixtures \
  --objective "design system tokens" \
  --category design-system
```

Captain-local cache / live Stars:

```bash
"$CONTROL/scripts/northstar" skills refresh --repo "$SANDBOX"
"$CONTROL/scripts/northstar" skills learn \
  --repo "$SANDBOX" --source ti-cache --objective "schema validation"
# or:
"$CONTROL/scripts/northstar" skills learn \
  --repo "$SANDBOX" --source live --objective "schema validation"
```

Artifacts (under `--repo` / sandbox or control root as configured):

- Staging candidates: `.agent/capabilities/candidates/staging/`
- TI scorecards: `.agent/evidence/ti-scorecards/<id>/`
  (`security-review.md`, `dependency-supply-chain.md`, `scorecard.json`)
- Unified drafts: `.agent/capabilities/candidates/skill-drafts/<slug>/`
- Improvement proposals (when similar): `.agent/capabilities/candidates/skill-improvement-proposals/<existing-slug>/`
- Harness evidence: `.agent/evidence/candidate-sandbox-test/`
- Learning-run report: `.agent/learning-runs/` (includes additive `ledger` block)

### B. New Skill drafts

When no existing Skill is similar enough, the loop emits `SKILL.md` +
`capability.yaml` under `skill-drafts/` **only after** scorecard evidence exists.
Review with the Captain, then promote via Skills `candidate-promotion` /
`skill-lifecycle` with `--captain-approved` before copying into `.cursor/skills/`.

### C. Improve existing Skills when processes are similar

When Jaccard/overlap similarity between the candidate and a live Skill exceeds the
threshold (default `0.28`), the loop writes a **skill-improvement-proposal**
targeting that Skill. Proposals never mutate live `SKILL.md`. Meta and
safety-critical Skills are excluded from automatic targeting.

1. Review the proposal JSON (suggested procedure lessons + provenance + evidence).
2. Captain decides whether to fold lessons into the existing Skill via PR.
3. Do **not** auto-apply proposals. Use Skill procedure **F** with `--captain-approved`.

### D. Captain gate for live promotion

```bash
"$CONTROL/scripts/northstar" skills promote \
  --repo "$SANDBOX" \
  --candidate <staging.json> \
  --stage AVAILABLE_SKILL \
  --evidence .agent/evidence/candidate-sandbox-test/<id>/sandbox-test.json,.agent/evidence/ti-scorecards/<id>/security-review.md,.agent/evidence/ti-scorecards/<id>/dependency-supply-chain.md \
  --captain-approved \
  --skill-slug <slug>
```

Equivalent:

```bash
"$CONTROL/scripts/promote-candidate.sh" --repo-root "$SANDBOX" \
  --candidate <staging.json> \
  --stage AVAILABLE_SKILL \
  --evidence .agent/evidence/candidate-sandbox-test/<id>/sandbox-test.json,.agent/evidence/ti-scorecards/<id>/security-review.md,.agent/evidence/ti-scorecards/<id>/dependency-supply-chain.md \
  --captain-approved \
  --skill-slug <slug>
```

Then open a Captain-reviewed PR to install. Never set `approved_for_execution: true`.

### E. Experience bridge → PROVEN (M20)

```bash
"$CONTROL/scripts/northstar" skills learn \
  --repo "$SANDBOX" --source fixtures \
  --objective "accessible react forms" --record-experiences

"$CONTROL/scripts/bridge-learning-experiences.sh" \
  --run .agent/learning-runs/<run-id>.json

"$CONTROL/scripts/bridge-learning-experiences.sh" \
  --run .agent/learning-runs/<run-id>.json \
  --promote-proven \
  --candidate .agent/capabilities/candidates/staging/<id>.json \
  --skill-slug react-engineering \
  --evidence .agent/evidence/candidate-sandbox-test/<id>/sandbox-test.json \
  --captain-approved
```

PROVEN still needs ≥2 successful Experiences and `--captain-approved`.

### F. Apply an improvement proposal (M20/M23)

```bash
# Draft only (default) — requires --captain-approved AND scorecard evidence_paths
"$CONTROL/scripts/apply-skill-improvement.sh" \
  --proposal .agent/capabilities/candidates/skill-improvement-proposals/<slug>/from-<id>.json \
  --captain-approved

# Append learned section to the live Skill (Captain only)
"$CONTROL/scripts/apply-skill-improvement.sh" \
  --proposal .agent/capabilities/candidates/skill-improvement-proposals/<slug>/from-<id>.json \
  --captain-approved \
  --apply-live
```

Live apply remains `--captain-approved` only. Proposals must carry
`security-review` + `dependency-supply-chain` evidence paths.

### G. Linear ledger sync (M24 — optional)

```bash
"$CONTROL/scripts/northstar" skills sync-ledger \
  --run .agent/learning-runs/<run-id>.json \
  --mode fixtures
# or link an existing Linear parent (never invents CAPTAIN_APPROVED):
"$CONTROL/scripts/northstar" skills sync-ledger \
  --run .agent/learning-runs/<run-id>.json \
  --mode link \
  --parent-issue-id OVA-5
```

See `docs/integrations/linear-skills-learning-loop.md`. Linear never originates
Captain approval.

## Output

- Learning-run JSON report (with `ledger` linkage block)
- Staging candidates at `SANDBOX_TESTED`
- New Skill drafts and/or improvement proposals
- TI scorecard evidence suitable for draft + promotion gates

## Prohibited actions

- Auto-installing into `.cursor/skills/`
- Auto-applying improvement proposals to live Skills (apply requires `--captain-approved`)
- Drafting Skills without security-review + dependency-supply-chain evidence
- Ingesting non-starred external repos into TI
- Setting `approved_for_execution: true`
- Cloning or executing starred/external repositories
- Running the loop from hooks, workstream close, or CI defaults
- Advancing past `SANDBOX_TESTED` without `--captain-approved`
- Assuming learning scripts exist inside product/sandbox checkouts
- Treating Linear status as Captain approval
