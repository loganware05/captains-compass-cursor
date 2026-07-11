# Captain's Compass Cursor

Reusable **Cursor IDE** agentic engineering workflow template.

This is a **control repository**. It owns rules, Skills, subagents, hooks, document templates, and install scripts. Product application code does not live here. Install a smaller workflow package into each product repository.

**GitHub template:** https://github.com/loganware05/captains-compass-cursor

## Current version: 0.3.1

### Included

- Five always-applied core rules
- Twelve Skills (foundational + GitHub, React, Playwright, Node, Postgres/Prisma)
- Eight specialist subagents
- Seven documentation templates
- Seven hooks (secrets, protected branch, plan approval, branch-name, format, pre-push tests, PR evidence)
- `scripts/install.sh` and `scripts/doctor.sh`
- Example fixture (`examples/react-node-prisma/`)
- Automated installer / doctor / hook tests

### Not included yet

- Linear / Notion / cloud MCP stages
- Docker, Python/ML, iOS Skills (Docker/cloud starts in V0.4)
- Automatic updates that overwrite project customizations
- Overnight autonomy / auto-merge / production deploys

## Operating model

- **Captain** — you (human). Approves plans and merges.
- **First Mate** — primary Cursor agent. Discovers, plans, coordinates, verifies.
- **Approval gate** — agents may investigate and write `IMPLEMENTATION_PLAN.md`, but must not change product implementation files until the plan status is **APPROVED** (also enforced by the plan-approval hook).

## Quick start (control repo)

```bash
./scripts/doctor.sh
./tests/run.sh
```

## Install into a product repository

Prefer a **disposable sandbox** before any important project:

```bash
./scripts/install.sh /path/to/product-repo
./scripts/install.sh --force /path/to/product-repo   # refreshes .cursor only; keeps product docs
```

Control repository (private template): https://github.com/loganware05/captains-compass-cursor

After install, the product repo should contain:

- `.cursor/rules/`, `.cursor/skills/`, `.cursor/agents/`, `.cursor/hooks/`, `.cursor/hooks.json`
- `.agent/evidence/`
- Root memory docs (`AGENTS.md`, `PROJECT_CONTEXT.md`, …)

## GitHub (Stage 1)

```bash
gh auth login
```

See [`docs/integrations/github.md`](docs/integrations/github.md).

## Node / Postgres / Prisma (V0.3)

See [`docs/integrations/node-postgres-prisma.md`](docs/integrations/node-postgres-prisma.md).

## Design documents

Source design material lives under [`docs/design/`](docs/design/) and is **not** installed into product repos.

## License

See [LICENSE](LICENSE).
