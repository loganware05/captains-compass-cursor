# M23 TI Scorecard + Skill Flywheel — Validation

**Date:** 2026-09-10  
**Branch:** `cursor/m23-ti-skill-flywheel-6044`  
**Plan:** `m22-m23-northstar-ops-ti-flywheel` (Captain APPROVED; M23 start directed)  
**Rollback:** `rollback/pre-m23-ti-flywheel`  
**VERSION:** `1.28.0`

## Commands

```bash
./scripts/doctor.sh
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m23_ti_skill_flywheel -v
./tests/run.sh
./scripts/example-design-repo-scorecard.sh
```

## Results (pre-commit)

| Check | Result |
|---|---|
| `design-system` in `DEFAULT_CATEGORIES` + manual labels | Pass |
| Starred provenance reject non-starred feed | Pass |
| Draft gate requires security-review + supply-chain | Pass |
| Scorecard → draft keeps `approved_for_execution: false` | Pass |
| Learning loop `--category design-system` | Pass |
| Example design-repo scorecard script | Pass — see `example-design-repo-scorecard.json` |
| Focused related suites (m14/m19/m20/promotion) | Pass (37) |

## Fail-closed checks

- Non-starred external repo ingest rejected
- Skill draft without both evidence kinds rejected
- Live Skill apply still requires `--captain-approved`
- No clone/exec of starred repos from TI/learning
- Slack/Linear never approve (unchanged from M22)

## Sandbox UI experiment

Bounded craft-tokens demo lands in `captain-compass-sandbox` only.
Evidence: sandbox `.agent/evidence/m23-craft-tokens/` (a11y/vitest).
Linked from `docs/SANDBOX_VALIDATION.md`.

## Gaps / deferred

- Control **v1.28.0** tag/release pending Captain merge
- Sandbox refresh PR `cursor/refresh-compass-1.28.0-6044` after control push

## Rollback

```bash
git checkout rollback/pre-m23-ti-flywheel
```
