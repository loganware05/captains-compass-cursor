# PostgreSQL MCP (Stage 6)

Use with the `postgres-prisma` Skill.

## Enable gradually

- Development databases only by default
- Read-only access during planning
- Explicitly separated development and production credentials

## Agent behavior

- Prefer Prisma migrations and schema reviews in the product repo
- Do not run destructive production SQL without Captain approval
- Keep connection strings in env files (gitignored); document names in `.env.example`

## Related

- Skill: `.cursor/skills/postgres-prisma/SKILL.md`
- Stage 5 cloud limits: `docs/integrations/cloud-mcp.md`
