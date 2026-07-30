# Validation — v1.1.0 release/tag repair (#23)

- Date: 2026-07-30
- Branch: `feature/23-repair-v1.1.0-release`
- Control rollback: `rollback/pre-v1.1.0-release-repair` (`e838f45`)
- Intended v1.1.0 commit: `a6b2aae` (merge of PR #20)

## Pre-repair validation

- `VERSION` at intended commit: `1.1.0`
- `./scripts/doctor.sh`: PASS (0 errors, 0 warnings)
- `./tests/run.sh`: PASS (52/52)
- Rollback tag `rollback/pre-micky-inspired-skills`: `2dd5429`
- `v1.1.0` was absent before repair

## Release repair

- Annotated local/remote `v1.1.0` tag: PASS
- Peeled `v1.1.0` commit: `a6b2aae6be3c5f4e632561198b3499992075ffd2`
- Local/remote peeled commits match: PASS
- GitHub release:
  - name: `v1.1.0 — Micky-inspired Skills`
  - `tagName`: `v1.1.0`
  - URL: https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.1.0
- Malformed release attached to `rollback/pre-micky-inspired-skills`: removed
- Rollback Git tag `rollback/pre-micky-inspired-skills`: preserved
- Release audit `v1.1.0` through `v0.2.0`: no other `rollback/*` releases
- README latest-stable selector now resolves to `v1.1.0`
- Hardened release checklist Bash/zsh syntax: PASS
- Adversarial review: PASS; no blocking or remaining findings
- Raw transcripts:
  - `control-validation.txt`
  - `release-state.txt`
  - `sandbox-validation.txt`

## Sandbox refresh

- Issue: https://github.com/loganware05/captain-compass-sandbox/issues/5
- PR: https://github.com/loganware05/captain-compass-sandbox/pull/6
- Source: repaired tag `v1.1.0` (`a6b2aae`)
- Compass doctor: PASS
- `npm test`: PASS (15/15)
- Product memory hashes unchanged during installer refresh
- No product implementation files changed
- Sandbox rollback: `rollback/pre-compass-v1.1.0-refresh` (`67c049e`)

## Rollback review

- Public repair rollback: delete release `v1.1.0`, then delete local/remote
  `v1.1.0` tag only if necessary.
- Preserve `rollback/pre-micky-inspired-skills`.
- Checklist/docs rollback: revert the control PR.
- Sandbox rollback: revert sandbox PR #6 or use its rollback tag.
