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
- **Technology Intelligence adapter** — stub provider + integration contract (`docs/integrations/technology-intelligence.md`); no external repo coupling in M1

## Repository Map

- `.cursor/` — reusable rules, Skills, agents, hooks (source of truth)
- `orchestrator/` — capability schemas, registry compiler (M1), planning pipeline (v1.5.0+)
- `templates/docs/` — blank docs installed into product repos
- `scripts/` — install.sh, update.sh, uninstall.sh, doctor.sh
- `examples/` — fixture projects for installer docs/tests
- `tests/` — automated installer/doctor/hook tests
- `docs/` — onboarding, agent install/activation prompts, upgrading, release checklist, integrations, design sources

## Major Components

1. AGENTS.md operating contract
2. Five always-applied core rules
3. Thirty-eight Skills (including embedding-providers, package-registry-ti, external-knowledge-ingest, skill-lifecycle, procedure-playbooks, knowledge-steward, technology-intelligence-live, persistent-role-promotion, bounded-autonomy, compass-evaluator, experience-routing, capability-planning, execution-telemetry, candidate-promotion, experience-skill-training)
4. Ten specialist subagents (including `compass-evaluator`, `knowledge-steward`)
5. Seven safety hooks (three critical fail-closed; four soft fail-open with multi-path skips)
6. Six Cursor phase commands under `.cursor/commands/`
7. Documentation, budget/session templates, evidence matrix, multi-runtime adapters, evals
8. Installation, update, uninstall, and doctor scripts
9. Control-repo CI (doctor + tests + harness evals)
10. **Orchestrator module** (`orchestrator/`) — planning (v1.5.0+), telemetry/file TI (v1.6.0), evaluator/routing/proficiency (v1.7.0 M3), persistent roles + bounded weight apply (v1.8.0 M4), knowledge steward (v1.9.0 M5), hybrid vector search (v1.10.0 M6), performance knowledge + live Stars TI (v1.11.0 M7), procedure ingest + TI cache (v1.12.0 M8), skill lifecycle + Artifact Context (v1.13.0 M9), external knowledge + HF file TI (v1.14.0 M10), fixture embeddings + package-registry file TI (v1.15.0 M11)

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

None blocking. Hosted vector DBs and live embedding/registry HTTP remain deferred.

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

M12 / v1.16.0 shipped. Post-foundation backlog **APPROVED** — M13 in progress (Neon/pgvector, namespaces). See `IMPLEMENTATION_PLAN.md`.
