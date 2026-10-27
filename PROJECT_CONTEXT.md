# Project Context

## Product Summary

Captain's Compass is a reusable Cursor IDE engineering workflow template,
rebranded for M21+ as **NorthStar** (Captain's Compass remains the compatibility
alias). It is a control repository: it owns rules, Skills, subagents, hooks,
document templates, and installation scripts. Product application code does not
live here.

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
3. Forty-seven Skills (including Wave 1 Stars-derived `agent-skills-packaging`,
   `goose-agent-orchestration`, `security-audit-procedures`, plus
   `project-overseer`, `code-reviewer`, `context-inodes`,
   northstar-connected-routine, skill-learning-loop, embedding-providers,
   package-registry-ti, external-knowledge-ingest, skill-lifecycle,
   procedure-playbooks, knowledge-steward, technology-intelligence-live,
   persistent-role-promotion, bounded-autonomy, compass-evaluator,
   experience-routing, capability-planning, execution-telemetry,
   candidate-promotion, experience-skill-training).
   `.cursor/skills/inodes/` is the context-inode content store (not a Skill).
4. Twelve specialist subagents (including `project-overseer`, `code-reviewer`, `compass-evaluator`, `knowledge-steward`)
5. Seven safety hooks (three critical fail-closed; four soft fail-open with multi-path skips)
6. Six Cursor phase commands under `.cursor/commands/`
7. Documentation, budget/session templates, evidence matrix, multi-runtime adapters, evals
8. Installation, update, uninstall, and doctor scripts
9. Control-repo CI (doctor + tests + harness evals)
10. **Orchestrator module** (`orchestrator/`) — planning (v1.5.0+), telemetry/file TI (v1.6.0), evaluator/routing/proficiency (v1.7.0 M3), persistent roles + bounded weight apply (v1.8.0 M4), knowledge steward (v1.9.0 M5), hybrid vector search (v1.10.0 M6), performance knowledge + live Stars TI (v1.11.0 M7), procedure ingest + TI cache (v1.12.0 M8), skill lifecycle + Artifact Context (v1.13.0 M9), external knowledge + HF file TI (v1.14.0 M10), fixture embeddings + package-registry file TI (v1.15.0 M11), **code review pipeline (v1.30.0 M27)**, **filesystem-gated context (v1.41.0 M40)**, **optional DecisionProvider / Jev shadow skill suggestion (v1.42.0 M41)**, **behavior loop M46–M54 (evaluate → learn → instructions → prompt-eval → policy promotion → Project Overseer status/Skill → provenance + exemplars → operator closure wiring)**, **Cognitive Core C1 project-state / `northstar brain` (v1.60.0)**, **Cognitive Core C2 memory/retrieval / `brain context` (v1.61.0)**, **Cognitive Core C3 difficulty / `assess project` (v1.62.0)**, **Cognitive Core C4 adaptive cycle / `cycle` + `learning review` (v1.63.0)**, **Cognitive Core C5 adaptive routing / `model route|evaluate` (v1.64.0)**, **Cognitive Core C6 REA / `rea investigate` (v1.65.0)**, **Cognitive Core C7 Training bridge / `train export|review` (v1.66.0)**, **Cognitive Core e2e evaluation / `cognitive e2e` (v1.67.0)**, **read-only persistent oversight / `oversight run` (v1.68.0)**

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
- **Track namespaces** — milestone IDs must carry a track prefix in prose when
  ambiguous: `roadmap/*` (historical continuation / product install),
  `cognitive/*` (Cognitive Core C1–C7), `specialized/*` (model levels),
  `consolidation/*` (N1–N3). Example: `roadmap/C2` product-repo install ≠
  `cognitive/C2` memory retrieval.

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

**N5 Skill-Fit / Routing Feedback** shipping as **v1.76.0**
(`northstar feedback n5`). N4 COMPLETE at **v1.75.0** (#243).
Open UI Control Plane COMPLETE (**v1.74.0** / #241; hotfix **v1.74.1**).
N3 COMPLETE at **v1.73.0**; N2 COMPLETE at **v1.72.0**; N1 COMPLETE at
**v1.71.1**. Specialized Model Level 3 remains **DEFERRED**. Behavior Loop
(M46–M54) remains complete at **v1.59.0**. Start here:
`docs/guides/captain-handbook.md`.
Live trading / AHF execution remains denied.
