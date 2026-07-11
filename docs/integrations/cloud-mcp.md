# Cloud MCP (Stage 5)

Build on the `docker-cloud` Skill. Cloud MCP should start **read-only / preview-only**.

## Enable gradually

1. Read-only project inspection
2. Preview deployment creation
3. Deployment log access

## Keep approval-gated

- Production deploys
- Destroying environments
- Changing DNS / TLS / IAM broadly
- Applying unrestricted IaC to production

## Agent behavior

- Prefer preview URLs and log capture under `.agent/evidence/deployment/`
- Record rollback (previous image/revision) in IMPLEMENTATION_PLAN.md
- If MCP is unavailable, use CLI docs the Captain provides—do not invent cloud credentials

## Related

- Skill: `.cursor/skills/docker-cloud/SKILL.md`
- Example: `examples/docker-cloud/`
