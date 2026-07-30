# Changelog

## Unreleased

### Changed

- README and `docs/UPGRADING.md` document latest/pinned forward upgrades using
  tagged detached worktrees, version verification, product PR review, and the
  unsupported-downgrade boundary (#21)
- `docs/RELEASE_CHECKLIST.md` verifies stable tag names, intended/remote commit
  identity, and GitHub release `tagName` before declaring a release complete
  (#23)

### Fixed

- Replaced the malformed v1.1.0 GitHub release attached to
  `rollback/pre-micky-inspired-skills` with an annotated `v1.1.0` tag/release on
  the PR #20 merge commit; the rollback tag remains intact (#23)

## 1.1.0 — 2026-07-28

### Added

- `source-code-context` Skill — search real package/repo source before guessing APIs (prefer optional [opensrc](https://github.com/vercel-labs/opensrc))
- `code-structure-cleanup` Skill — post-feature service-layer cleanup under a **separate** approved plan
- `review-fix-loop` Skill — iterate on PR/review feedback until merge-ready or a human decision
- `docs/integrations/opensrc.md` — preferred-optional opensrc setup and fallbacks
- `docs/AGENT_INSTALL_PROMPT.md` — copy-paste agent prompts for install and post-install activation (PROJECT_CONTEXT interview)
- `docs/PRODUCT_ONBOARDING.md` — new vs existing product-repo install paths
- Sandbox failure-test evidence (bypass, scope, failing test, secret, parallel, budget)

### Changed

- VERSION `1.1.0`; doctor/tests expect twenty Skills
- README links to product onboarding, agent install prompts, and opensrc docs
- Project memory reflects v1.1.0 priorities and ADR-013

## 1.0.0 — 2026-07-11

### Added

- `scripts/update.sh` for safe product-repo refreshes
- `scripts/uninstall.sh` (requires `--yes`; optional `--purge-docs`)
- `docs/UPGRADING.md` and `docs/RELEASE_CHECKLIST.md`
- PostgreSQL MCP Stage 6 guidance (`docs/integrations/postgres-mcp.md`)

### Changed

- Declares the first **stable** reusable workflow release
- README documents update/uninstall paths
- Doctor/tests cover update/uninstall scripts

## 0.7.0 — 2026-07-11

### Added

- `ios-engineering` Skill for Swift/SwiftUI workflows
- `docs/integrations/ios.md` and `examples/ios/` placeholder

### Changed

- Doctor/tests expect the iOS Skill
- VERSION bumped to 0.7.0

## 0.6.0 — 2026-07-11

### Added

- `python-ml` Skill for Python services and reproducible ML workflows
- Cloud MCP Stage 5 guidance (`docs/integrations/cloud-mcp.md`)
- `docs/integrations/python-ml.md` and `examples/python-ml/` fixture
- Stacked-PR caution in GitHub integration docs

### Changed

- Doctor/tests expect the Python/ML Skill
- VERSION bumped to 0.6.0

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
