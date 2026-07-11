# Changelog

## 0.5.0 — 2026-07-11

### Added

- `linear-integration` Skill (MCP Stage 3)
- `notion-integration` Skill (MCP Stage 4)
- Docs: `docs/integrations/linear.md`, `docs/integrations/notion.md`

### Changed

- Doctor and installer tests expect Linear/Notion Skills
- VERSION bumped to 0.5.0

## 0.4.0 — 2026-07-10

### Added

- `docker-cloud` Skill for Dockerfiles, Compose, preview deploys, and rollback notes
- `docs/integrations/docker-cloud.md`
- Illustrative `examples/docker-cloud/` Compose + Dockerfile fixture

### Changed

- Doctor and installer tests expect the Docker/cloud Skill
- VERSION bumped to 0.4.0

## 0.3.1 — 2026-07-10

### Added

- Remaining hooks: branch-name validation, pre-commit formatting, pre-push tests, PR evidence validation
- Shared hook helpers (`.cursor/hooks/_common.sh`) for cwd-aware repo resolution

### Changed

- `hooks.json` registers all seven safety hooks
- Doctor and installer tests cover the new hooks

## 0.3.0 — 2026-07-10

### Added

- `node-engineering` Skill for Node.js APIs, auth boundaries, and integration tests
- `postgres-prisma` Skill for PostgreSQL/Prisma schema, migrations, and rollback notes
- `docs/integrations/node-postgres-prisma.md`
- Illustrative Prisma schema under `examples/react-node-prisma/`

### Changed

- Doctor and installer tests expect the V0.3 Skills
- VERSION bumped to 0.3.0

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
