---
name: node-engineering
description: Implements Node.js services, REST/GraphQL APIs, auth boundaries, validation, and integration tests
---

# Node.js Engineering

## Use this Skill when

Working on Node.js backends, API routes, middleware, background jobs, authentication/authorization, request validation, logging, or server integration tests.

## Inputs

- Approved IMPLEMENTATION_PLAN.md
- Existing server framework (Express, Fastify, Next.js route handlers, etc.)
- Auth and environment conventions from PROJECT_CONTEXT.md

## Procedure

1. Match existing project patterns (framework, folder layout, error shape).
2. Keep handlers thin; put business logic in clear modules/services.
3. Validate inputs at the boundary; return consistent error responses.
4. Enforce authentication and authorization on protected routes.
5. Never hard-code secrets; use environment variables / secret managers.
6. Add structured logging for failures without leaking sensitive data.
7. Add or update integration tests for changed endpoints and failure paths.
8. Document new env vars in `.env.example` and PROJECT_CONTEXT.md / TESTING.md.

## Output

Changed server files, tests, and any env/docs updates reported to the First Mate.

## Prohibited actions

- Do not weaken auth checks to make tests pass.
- Do not commit `.env` files or credentials.
- Do not expand into unrelated frontend or infrastructure refactors unless the approved plan includes them.
