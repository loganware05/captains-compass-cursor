---
name: security-review
description: Reviews changes for auth, secrets, injection, and other security risks
---

# Security Review

## Use this Skill when

Reviewing any change that touches authentication, authorization, input handling,
secrets, networking, file operations, dependencies, or cloud permissions.

## Inputs

- Diff / changed files
- Approved plan security section
- Environment and secret handling conventions

## Procedure

1. Check authentication and authorization boundaries.
2. Check input validation and injection risks.
3. Scan for committed secrets, keys, and credentials.
4. Review dependency and supply-chain risk for new packages.
5. Review unsafe file, deserialization, and network patterns.
6. Review container/cloud permission changes when present.
7. Record findings with severity and remediation.

## Output

Security review report under .agent/evidence/security/ when possible.

## Prohibited actions

- Do not hard-code secrets "for convenience."
- Do not commit .env files or private keys.
- Do not dismiss high-severity findings without Captain approval.
