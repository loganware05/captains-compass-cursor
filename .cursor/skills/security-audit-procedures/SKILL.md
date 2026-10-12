---
name: security-audit-procedures
description: Runs structured security-audit checklists for agent workflows and Skill promotions alongside security-review
---

# Security Audit Procedures

## Use this Skill when

Performing a structured security audit of agent workflows, Skill promotions,
hooks, or TI/learning artifacts — complementary to Skill `security-review`.

## Origin

- Starred discovery: [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill)
- Candidate: `github-stars-cloudflare-security-audit-skill`
- Lifecycle: `AVAILABLE_SKILL` (Captain-promoted Wave 1 / OVA-71)
- **Metadata/procedure only** — do not clone or execute the starred repo

## Inputs

- Diff / changed files or Learning Loop candidate package
- TI scorecards when promoting Stars-derived Skills
- Hook / control-plane change set when applicable

## Procedure

1. Confirm trust boundary: discovery signal vs executable dependency.
2. For Stars-derived Skills, require M23 scorecards
   (security-review + dependency-supply-chain) before AVAILABLE proposals.
3. Check secrets handling, path traversal, and unsafe shell/git patterns in
   scripts and hooks.
4. Verify promotions never set `approved_for_execution: true` on TI candidates
   and never auto-install into `.cursor/skills/`.
5. For control-plane changes, cross-check Skill `security-review` fail-closed
   items (plan-approval, protected branch, soft-hook skips).
6. Record findings under `.agent/evidence/security/` with severity and remediation.

## Output

- Security audit notes / evidence markdown
- Go/no-go for Skill promote or PR merge

## Prohibited actions

- Do not clone or execute the starred audit toolkit
- Do not weaken fail-closed hooks to pass an audit
- Do not treat Linear/Overseer status as Captain approval
