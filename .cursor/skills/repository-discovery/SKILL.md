---
name: repository-discovery
description: Performs read-only repository discovery and reports architecture, tooling, risks, and conventions
---

# Repository Discovery

## Use this Skill when

Starting a new task, onboarding to an unfamiliar repository, or before writing an implementation plan.

## Inputs

- Repository root
- Existing project documentation
- Git status

## Procedure

1. Identify languages, frameworks, and runtime versions.
2. Identify package managers and build tooling.
3. Map repository structure and application entry points.
4. Identify test frameworks and CI/CD.
5. Identify database and deployment configuration.
6. Note existing Cursor instructions (AGENTS.md, rules, Skills).
7. List high-risk files and missing documentation.
8. Recommend Skills relevant to the current task.

## Output

A structured repository-discovery report for the First Mate.

## Prohibited actions

- Do not modify product files.
- Do not install dependencies without approval.
- Do not rewrite documentation during discovery.
