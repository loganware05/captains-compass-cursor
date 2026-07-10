# Changelog

## 0.2.0 — 2026-07-10

### Added

- GitHub Stage 1 Skill (`github-integration`) and setup doc (`docs/integrations/github.md`)
- React engineering Skill
- Playwright / browser validation Skill
- First three project hooks: secret protection, protected-branch, plan-approval check
- `.cursor/hooks.json` installed into product repos

### Changed

- `pull-request-preparation` Skill uses GitHub when authenticated, local PR-ready fallback otherwise
- `install.sh` / `doctor.sh` / tests cover hooks and new Skills
- `--force` refreshes `.cursor/` package but **preserves** existing product memory docs

## 0.1.0 — 2026-07-10

### Added

- Core always-applied Cursor rules (5)
- Foundational Skills (7)
- Initial subagents (8)
- Documentation templates for product repos
- `scripts/install.sh` and `scripts/doctor.sh`
- Example fixture under `examples/react-node-prisma/`
- Automated installer and doctor tests
- Root project memory documents for the control repository
