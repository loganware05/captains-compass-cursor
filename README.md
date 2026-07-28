# Captain's Compass Cursor

Reusable **Cursor IDE** agentic engineering workflow template.

**GitHub template:** https://github.com/loganware05/captains-compass-cursor

This is a **control repository**. It owns rules, Skills, subagents, hooks, document templates, and scripts. Product application code does not live here.

## Current version: 1.0.0 (stable)

### Included

- Approval-gated operating model (`AGENTS.md` + five core rules)
- Seventeen Skills (foundational + GitHub, React, Playwright, Node, Postgres/Prisma, Docker/cloud, Linear, Notion, Python/ML, iOS)
- Eight specialist subagents
- Seven safety hooks
- `install.sh`, `update.sh`, `uninstall.sh`, `doctor.sh`
- Documentation templates and integration guides
- Automated installer / doctor / hook tests

### Operating model

- **Captain** — human owner; approves plans and merges
- **First Mate** — coordinating Cursor agent
- **Approval gate** — no product implementation changes until `IMPLEMENTATION_PLAN.md` is **APPROVED**

## Quick start (control repo)

```bash
./scripts/doctor.sh
./tests/run.sh
```

## Install into a product repository

Full guide (new vs existing projects): [`docs/PRODUCT_ONBOARDING.md`](docs/PRODUCT_ONBOARDING.md).

Copy-paste Cursor agent prompts (install + activate / fill `PROJECT_CONTEXT.md`): [`docs/AGENT_INSTALL_PROMPT.md`](docs/AGENT_INSTALL_PROMPT.md).

```bash
./scripts/install.sh /path/to/product-repo
```

## Update an existing install

```bash
./scripts/update.sh /path/to/product-repo
```

See [`docs/UPGRADING.md`](docs/UPGRADING.md).

## Uninstall

```bash
./scripts/uninstall.sh --yes /path/to/product-repo
```

## Integrations

| Area | Doc |
|---|---|
| GitHub | [`docs/integrations/github.md`](docs/integrations/github.md) |
| Node / Postgres / Prisma | [`docs/integrations/node-postgres-prisma.md`](docs/integrations/node-postgres-prisma.md) |
| Docker / cloud | [`docs/integrations/docker-cloud.md`](docs/integrations/docker-cloud.md) / [`cloud-mcp.md`](docs/integrations/cloud-mcp.md) |
| Linear / Notion | [`linear.md`](docs/integrations/linear.md) / [`notion.md`](docs/integrations/notion.md) |
| Python / ML | [`docs/integrations/python-ml.md`](docs/integrations/python-ml.md) |
| iOS | [`docs/integrations/ios.md`](docs/integrations/ios.md) |
| Postgres MCP | [`docs/integrations/postgres-mcp.md`](docs/integrations/postgres-mcp.md) |

## Releases

See [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) and [`CHANGELOG.md`](CHANGELOG.md).

## License

See [LICENSE](LICENSE).
