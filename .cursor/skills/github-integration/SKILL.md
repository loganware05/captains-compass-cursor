---
name: github-integration
description: Creates issues and pull requests with GitHub CLI or MCP when authenticated; falls back locally when unavailable
---

# GitHub Integration (Stage 1)

## Use this Skill when

Creating or updating issues, opening pull requests, commenting on PRs, or checking CI status for an approved change.

## Prerequisites

Prefer authenticated GitHub CLI:

```bash
gh auth status
# if needed:
gh auth login
```

Cursor GitHub MCP may also be enabled with repository read, issue create, PR create/comment, and CI status. Do **not** enable automatic merges or releases in Stage 1.

## Procedure

1. Check `gh auth status` (or GitHub MCP availability).
2. If authenticated:
   - Create or reference a real GitHub issue for the workstream.
   - Push the feature branch.
   - Open a pull request with the prepared title/body and evidence links.
   - Optionally inspect CI status; do not auto-merge.
3. If **not** authenticated:
   - Use a documented local issue placeholder (e.g. `local/<slug>`).
   - Write a PR-ready description into the completion report / chat.
   - Tell the Captain that remote issue/PR creation is blocked on GitHub auth.
   - Do **not** treat missing remote PR as a Definition-of-Done failure in V0.2.

## Allowed Stage 1 capabilities

- Repository reads
- Issue creation
- Pull-request creation and comments
- CI status inspection

## Prohibited actions

- Automatic merges
- Automatic releases
- Production deploys via GitHub Actions without Captain approval
