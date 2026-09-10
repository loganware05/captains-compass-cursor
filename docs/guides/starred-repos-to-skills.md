# Captain guide: GitHub Stars → NorthStar Skills

Use this after **v1.28.0** (M23). External repos become Skills only through
explicit Captain gates. NorthStar never clones, installs, or executes starred
repos automatically.

## What “using a Star as a Skill” means

1. **Discover** — your starred repos enter Technology Intelligence (TI).
2. **Categorize** — fixed usefulness labels (`frontend-ui`, `design-system`, …).
3. **Scorecard** — security-review + dependency-supply-chain evidence (required).
4. **Draft** — staging Skill draft or improvement proposal (not live yet).
5. **Promote** — you approve a PR that copies the draft into `.cursor/skills/`.

Staging artifacts ≠ installed Skills.

## Prerequisites

- Work in **`captain-compass-sandbox`** (or control repo for fixture dry-runs).
- Compass **≥ 1.28.0** installed (`./scripts/doctor.sh`).
- `gh` authenticated as you (`gh auth status`) for live Stars.
- Star the repos you want to learn from on GitHub first.

## Path A — Dry run (fixtures, no network)

From the control or sandbox Compass install:

```bash
./scripts/example-design-repo-scorecard.sh
# or:
./scripts/run-skill-learning-loop.sh \
  --source fixtures \
  --objective "design system tokens" \
  --category design-system
```

Inspect:

- `.agent/evidence/ti-scorecards/`
- `.agent/capabilities/candidates/skill-drafts/`
- `.agent/learning-runs/`

## Path B — Your real Stars (recommended)

### 1. Refresh the starred-repos cache

```bash
./scripts/refresh-ti-cache.sh
# or skip if fresh within 24h:
./scripts/refresh-ti-cache.sh --if-stale 24
```

Cache: `.agent/intelligence/ti-cache/starred-repos.json`

### 2. Categorize (optional but recommended)

```bash
./scripts/categorize-github-stars.sh --source ti-cache
```

Labels live under `.agent/intelligence/` / TI label fixtures. Adjust manual
labels for high-value repos (e.g. mark a design toolkit `design-system`).

### 3. Query / learn against an objective

```bash
# Read-only TI peek
COMPASS_TI_PROVIDER=github-stars-cached \
  ./scripts/query-technology-intelligence.sh --query "accessible forms"

# Full learning loop (cache)
./scripts/run-skill-learning-loop.sh \
  --source ti-cache \
  --objective "accessible react forms" \
  --category frontend-ui

# Or live Stars (requires gh)
./scripts/run-skill-learning-loop.sh \
  --source live \
  --objective "design system tokens" \
  --category design-system
```

### 4. Review scorecards before trusting a draft

For each candidate under `.agent/evidence/ti-scorecards/<id>/`:

- `security-review.md` — threat notes, trust boundary, what you refuse to import
- `dependency-supply-chain.md` — deps/lockfile posture, known risk
- `scorecard.json` — machine summary

Missing either review → Skill draft **fails closed**.

### 5. Promote only with your approval

```bash
./scripts/promote-candidate.sh --candidate <staging.json> \
  --stage AVAILABLE_SKILL \
  --evidence .agent/evidence/candidate-sandbox-test/<id>/sandbox-test.json,.agent/evidence/ti-scorecards/<id>/security-review.md,.agent/evidence/ti-scorecards/<id>/dependency-supply-chain.md \
  --captain-approved \
  --skill-slug <slug>
```

Then open a **PR** that copies draft files into `.cursor/skills/<slug>/`.
Do **not** set `approved_for_execution: true` on TI candidates.

### 6. Improve an existing Skill (instead of a new one)

When the loop finds a similar live Skill, it writes a proposal under
`.agent/capabilities/candidates/skill-improvement-proposals/`.

```bash
# Review, then draft apply
./scripts/apply-skill-improvement.sh \
  --proposal <proposal.json> \
  --captain-approved

# Append to live Skill (still Captain-only; prefer via PR)
./scripts/apply-skill-improvement.sh \
  --proposal <proposal.json> \
  --captain-approved \
  --apply-live
```

## Suggested first session (concrete)

1. Star 3–5 repos you already trust (one design-system, one frontend lib, one tool).
2. In sandbox: `./scripts/refresh-ti-cache.sh`
3. Run loop with `--category design-system` or `frontend-ui` and a real objective.
4. Read the scorecard; tighten/reject anything you would not want in a Skill.
5. Promote **one** draft via PR into `.cursor/skills/` and use it on a sandbox task.
6. Optionally run with `--record-experiences` and later bridge toward `PROVEN_SKILL`.

## Hard rules (do not bypass)

| Rule | Why |
|---|---|
| Must be **starred** | TI provenance gate (M23) |
| Scorecard before draft | Security + supply-chain fail-closed |
| No clone/exec of external repos | Skills capture *procedure*, not vendor code |
| No auto-install to `.cursor/skills/` | Captain PR only |
| Sandbox product only (for this flywheel) | Contained blast radius |

## Related

- Skill: `.cursor/skills/skill-learning-loop/SKILL.md`
- Skill: `.cursor/skills/candidate-promotion/SKILL.md`
- Docs: `docs/integrations/technology-intelligence.md`
- Example: `./scripts/example-design-repo-scorecard.sh`
