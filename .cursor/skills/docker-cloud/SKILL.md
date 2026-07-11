---
name: docker-cloud
description: Implements Dockerfiles, Compose, preview deploys, health checks, and rollback-safe cloud configuration
---

# Docker and Cloud Previews

## Use this Skill when

Working on Dockerfiles, Docker Compose, container health checks, preview deployments, deployment manifests, or cloud configuration for non-production environments.

## Inputs

- Approved IMPLEMENTATION_PLAN.md (deployment + rollback sections)
- Existing Dockerfile / Compose / cloud config
- Environment separation from PROJECT_CONTEXT.md

## Procedure

1. Prefer the project's existing container and cloud conventions.
2. Keep images minimal and reproducible (pinned base tags when practical).
3. Separate build-time and runtime secrets; never bake secrets into images.
4. Add health checks and sensible restart policies for services that need them.
5. For cloud previews: create/update preview environments only; do not touch production without explicit Captain approval.
6. Capture deploy logs and URLs under `.agent/evidence/deployment/` when available.
7. Document required env vars in `.env.example` and TESTING.md / PROJECT_CONTEXT.md.
8. Write rollback steps (previous image tag, compose down, redeploy prior revision).

## Output

Dockerfile/Compose/cloud config changes, evidence paths, and rollback notes for the First Mate.

## Prohibited actions

- Do not deploy to production or run destructive cloud operations without Captain approval.
- Do not commit cloud credentials, kubeconfigs, or `.env` files.
- Do not expose debug ports or disable TLS "temporarily" in shared environments.
