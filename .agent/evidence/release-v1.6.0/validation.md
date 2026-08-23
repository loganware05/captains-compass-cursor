# v1.6.0 release prep validation

Date: 2026-08-23
Branch: `chore/41-release-v1.6.0`
Issue: #41
Feature PR: #42 (merged @ `ccd4e61`)

## Automated (this commit)

| Command | Result |
|---|---|
| `./scripts/doctor.sh` | 0 errors (see `doctor.txt`) |
| Orchestrator unittest | 75 passed (see `orchestrator-unittests.txt`) |
| `./tests/run.sh` | 111 passed, 0 failed (`tests.txt`) |
| `./tests/evals/run.sh` | 31 passed, 0 failed (`evals.txt`) |
| `./scripts/capability-plan.sh --plan-id release-v1.6.0-smoke "..."` | Required Capabilities, Task Graph, Approval Boundary, TI NOT APPROVED (`capability-plan-smoke-stdout.txt`) |
| `COMPASS_TI_PROVIDER=file ./scripts/capability-plan.sh ...` | Redacted Stars candidates + NOT APPROVED (`file-ti-smoke-stdout.txt`) |

VERSION file: `1.6.0`
CHANGELOG heading: `## 1.6.0 — 2026-08-23`

## After Captain merge (RELEASE_CHECKLIST)

- Merge release PR into `main`
- Detached worktree doctor + tests on `origin/main`
- Annotated tag `v1.6.0` on that commit
- `gh release create` using `v1.6.0-github-notes.md`
- `./scripts/update.sh` on captain-compass-sandbox
- Sandbox checklist: telemetry close + optional file TI demo
