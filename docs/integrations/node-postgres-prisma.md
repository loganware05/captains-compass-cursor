# Node.js, PostgreSQL, and Prisma (V0.3)

Captain's Compass V0.3 adds technology Skills for Node backends and Prisma/Postgres data changes.

## Skills installed

- `.cursor/skills/node-engineering/SKILL.md`
- `.cursor/skills/postgres-prisma/SKILL.md`

## When agents should load them

| Change type | Skill |
|---|---|
| API routes, middleware, jobs, auth | `node-engineering` |
| Prisma schema, migrations, indexes, seeds | `postgres-prisma` |
| React UI | `react-engineering` (V0.2) |
| Browser evidence | `playwright-browser-validation` (V0.2) |

## Safety

- Approval gate still applies before product file changes
- No production DB credentials in the repo
- Migrations require rollback notes in IMPLEMENTATION_PLAN.md
- Secrets stay in `.env` (gitignored) with `.env.example` documented

## Example fixture

See `examples/react-node-prisma/` for a minimal illustrative layout (not a runnable full stack in V0.3).
