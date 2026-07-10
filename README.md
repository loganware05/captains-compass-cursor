# Captain's Compass Cursor

Reusable **Cursor IDE** agentic engineering workflow template.

This is a **control repository**. It owns rules, Skills, subagents, hooks, document templates, and install scripts. Product application code does not live here. Install a smaller workflow package into each product repository.

## Current version: 0.2.0

### Included

- Five always-applied core rules
- Ten Skills (7 foundational + GitHub, React, Playwright)
- Eight specialist subagents
- Seven documentation templates
- First three hooks (secrets, protected branch, plan approval)
- `scripts/install.sh` and `scripts/doctor.sh`
- Example fixture (`examples/react-node-prisma/`)
- Automated installer / doctor / hook tests

### Not included yet

- Remaining hooks (branch-name, format, pre-push tests, PR evidence)
- Linear / Notion / cloud MCP stages
- Node, Prisma, Docker, Python/ML, iOS Skills
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
./scripts/install.sh --force /path/to/product-repo   # intentional overwrite
```

After install, the product repo should contain:

- `.cursor/rules/`, `.cursor/skills/`, `.cursor/agents/`, `.cursor/hooks/`, `.cursor/hooks.json`
- `.agent/evidence/`
- Root memory docs (`AGENTS.md`, `PROJECT_CONTEXT.md`, …)

## GitHub (Stage 1)

```bash
gh auth login
```

See [`docs/integrations/github.md`](docs/integrations/github.md). Without auth, agents use a local issue placeholder and a PR-ready description.

## Design documents

Source design material lives under [`docs/design/`](docs/design/) and is **not** installed into product repos.

## License

See [LICENSE](LICENSE).
