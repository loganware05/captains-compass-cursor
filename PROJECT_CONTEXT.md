# Project Context

## Product Summary

Captain's Compass is a reusable Cursor IDE engineering workflow template.
It is a control repository: it owns rules, Skills, subagents, hooks, document
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
- Product repos can update/uninstall without losing memory docs

## Current Technology Stack

- Cursor IDE (rules, Skills, subagents, hooks)
- Bash install / update / uninstall / doctor scripts
- Git / Git worktrees
- Markdown project memory documents
- Optional MCP integrations (GitHub, Linear, Notion, cloud, Postgres) documented under `docs/integrations/`

## Repository Map

- `.cursor/` — reusable rules, Skills, agents, hooks (source of truth)
- `templates/docs/` — blank docs installed into product repos
- `scripts/` — install.sh, update.sh, uninstall.sh, doctor.sh
- `examples/` — fixture projects for installer docs/tests
- `tests/` — automated installer/doctor/hook tests
- `docs/` — onboarding, agent install/activation prompts, upgrading, release checklist, integrations, design sources

## Major Components

1. AGENTS.md operating contract
2. Five always-applied core rules
3. Twenty-one Skills (foundational + tech/integration + source-context, cleanup, review-fix, autonomy-budget)
4. Eight specialist subagents
5. Seven safety hooks (three critical fail-closed; four soft fail-open)
6. Six Cursor phase commands under `.cursor/commands/`
7. Documentation, budget templates, evidence matrix, multi-runtime adapters
8. Installation, update, uninstall, and doctor scripts
9. Control-repo CI (doctor + automated tests)

## External Services

None required for core workflow. Optional GitHub CLI/MCP, opensrc CLI, and other
MCPs are documented per integration guide. GitHub Actions runs on this control repo.

## Environments

Local development and product-repo installs. GitHub template repository enabled.

## Deployment Targets

Not applicable. This repository is installed into other Git repositories.

## Security Boundaries

- Never commit secrets
- Never install into production product repos until sandbox validation passes
- Installer refuses overwrite unless `--force` is provided
- Update/uninstall must not destroy product memory docs by default

## Accessibility Expectations

Accessibility review Skill and subagent apply when installed into UI projects.

## Performance Expectations

Installer and doctor should complete in seconds on a typical laptop.

## Known Constraints

- Cursor agent behavior depends on the host IDE; scripts only provision files
- Control-repo scripts are not copied into product repos; run them from this repo
- Stacked PRs that merge to a feature base (not `main`) can leave versions off `main`

## Known Technical Debt

None blocking for v1.3.0 P1. Optional follow-ups: P2 evals/harness GC/session
ledger/structural tests/supply-chain; soft-hook `COMPASS_SKIP_*` env inheritance.

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
./scripts/update.sh /path/to/product-repo
./scripts/uninstall.sh --yes /path/to/product-repo
./tests/run.sh
gh auth status
```

## Local Development Setup

1. Clone this repository
2. Open it alone in Cursor
3. Run `./scripts/doctor.sh`
4. Run `./tests/run.sh`

## Current Priorities

P2 awaiting approval (evals, harness GC, session ledger, structural-test examples,
young-package supply-chain, soft-hook skip signaling) after v1.3.0 release.
