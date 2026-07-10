---
name: postgres-prisma
description: Designs and applies PostgreSQL/Prisma schema changes, migrations, indexes, and rollback-safe data updates
---

# PostgreSQL and Prisma

## Use this Skill when

Changing Prisma models, migrations, indexes, constraints, transactions, seed data, or PostgreSQL queries in a Node/Prisma project.

## Inputs

- Approved IMPLEMENTATION_PLAN.md (including migration/rollback sections)
- Existing `schema.prisma` and migration history
- Environment separation (dev vs production credentials)

## Procedure

1. Inspect current Prisma schema and recent migrations.
2. Prefer additive, backward-compatible changes when possible.
3. Define models, relations (both sides), indexes, and uniqueness explicitly.
4. Include `createdAt` / `updatedAt` on new models unless the project convention differs.
5. Generate migrations with the project's Prisma workflow (`migrate dev` locally; never invent irreversible production steps silently).
6. Write rollback notes (down migration strategy or restore steps) in the plan/evidence.
7. Validate queries and constraints; add seed updates only when required.
8. Keep production credentials out of the agent context; use development databases during planning/implementation.
9. Run applicable Prisma validate/generate and related tests before handoff.

## Output

Schema/migration files, seed updates if any, rollback notes, and validation evidence for the First Mate.

## Prohibited actions

- Do not run destructive production migrations without explicit Captain approval.
- Do not delete columns/tables without a migration and rollback plan.
- Do not store production connection strings in docs or commits.
