# v1.5.0 release prep validation

Date: 2026-08-19
Branch: `feature/35-m1-capability-aware-planning`
Issue: #35
PR: #36

## Automated (this commit)

| Command | Result |
|---|---|
| `./scripts/doctor.sh` | 0 errors (see `doctor.txt`) |
| Orchestrator unittest | OK (see `orchestrator-unittests.txt`) |
| `./tests/run.sh` | 104 passed, 0 failed (`tests.txt`) |
| `./tests/evals/run.sh` | 22 passed, 0 failed (`evals.txt`) |
| `./scripts/capability-plan.sh --plan-id release-v1.5.0-smoke "..."` | Required Capabilities, Task Graph, Approval Boundary, `react-engineering`, TI NOT APPROVED banner (`capability-plan-smoke.md`) |

VERSION file: `1.5.0`
CHANGELOG heading: `## 1.5.0 — 2026-08-19`

## After Captain merge (RELEASE_CHECKLIST)

- Merge PR #36 into `main`
- Detached worktree doctor + tests on `origin/main`
- Annotated tag `v1.5.0` on that commit
- `gh release create` using `v1.5.0-github-notes.md`
- `./scripts/update.sh` on `/Users/loganware/Documents/Personal/Code/captain-compass-sandbox`
- Interactive sandbox checklist row 7 (capability-aware `/plan-feature`)

Not done here: merge, tag, GitHub release, sandbox product update (Captain-gated).
