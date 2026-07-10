# Project Context

## Product Summary

Captain's Compass is a reusable Cursor IDE engineering workflow template.
It is a control repository: it owns rules, Skills, subagents, document
templates, and installation scripts. Product application code does not live here.

## Intended Users

Software engineers who use Cursor and want an approval-gated, evidence-based
agentic engineering process across multiple product repositories.

## Primary User Problems

- Agents implement before requirements are agreed
- Project context is lost between sessions
- Validation and evidence are inconsistent
- Workflow knowledge is duplicated or drifts across repos

## Success Metrics

- Agents pause at the implementation-plan approval gate
- Installer reliably provisions a product repo
- Doctor script detects missing or broken workflow files
- Sandbox feature exercise completes with evidence and a PR-ready branch

## Current Technology Stack

- Cursor IDE (rules, Skills, subagents)
- Bash install/doctor scripts
- Git / Git worktrees
- Markdown project memory documents

## Repository Map

- `.cursor/` — reusable rules, Skills, agents (source of truth)
- `templates/docs/` — blank docs installed into product repos
- `scripts/` — install.sh, doctor.sh
- `examples/` — fixture projects for installer tests
- `tests/` — automated installer/doctor tests
- `docs/design/` — source design documents (not installed)

## Major Components

1. AGENTS.md operating contract
2. Five always-applied core rules
3. Seven foundational Skills
4. Eight specialist subagents
5. Documentation templates
6. Installation and doctor scripts

## External Services

None required for Version 0.1. MCP integrations (GitHub, Linear, Notion, cloud)
are deferred.

## Environments

Local development only for V0.1.

## Deployment Targets

Not applicable. This repository is installed into other Git repositories.

## Security Boundaries

- Never commit secrets
- Never install into production product repos until sandbox validation passes
- Installer refuses overwrite unless `--force` is provided

## Accessibility Expectations

Accessibility review Skill and subagent apply when installed into UI projects.

## Performance Expectations

Installer and doctor should complete in seconds on a typical laptop.

## Known Constraints

- Version 0.1 excludes hooks, MCP, tech-specific Skills, and auto-updates
- Cursor agent behavior depends on the host IDE; scripts only provision files

## Known Technical Debt

None yet (initial release).

## Terminology

- **Captain** — human project owner
- **First Mate** — primary coordinating Cursor agent
- **Control repository** — this repo
- **Product repository** — an application repo that installs Compass
- **Approval gate** — no product file changes until IMPLEMENTATION_PLAN.md is APPROVED

## Important Commands

```bash
./scripts/doctor.sh
./scripts/install.sh /path/to/product-repo
./tests/run.sh
gh auth status   # GitHub Stage 1
```

## Local Development Setup

1. Clone this repository
2. Open it alone in Cursor
3. Run `./scripts/doctor.sh`
4. Run `./tests/run.sh`

## Current Priorities

Maintain V0.2.0; add remaining hooks and V0.3 Node/Prisma modules after sandbox re-validation.
