# Docker and Cloud Previews (V0.4)

Captain's Compass V0.4 adds guidance for containers and **preview** cloud deployments.

## Skill

- `.cursor/skills/docker-cloud/SKILL.md`

## Scope

| In scope | Out of scope (still approval-gated / later) |
|---|---|
| Dockerfiles and Compose | Automatic production releases |
| Health checks | Overnight autonomous deploys |
| Preview / staging deploys | Unrestricted cloud admin |
| Deploy evidence + rollback notes | Blind `terraform apply` to prod |

## Cloud MCP (Stage 5 — gradual)

When enabling cloud MCP later, start with:

- Read-only project inspection
- Preview deployment creation
- Deployment log access

Keep production destructive actions approval-gated.

## Example fixture

See `examples/docker-cloud/` for a minimal illustrative Compose layout.
