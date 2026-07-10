# GitHub Integration (Stage 1)

Captain's Compass Stage 1 enables issue and pull-request workflows without automatic merges.

## Setup (GitHub CLI)

```bash
brew install gh   # if needed
gh auth login
gh auth status
```

## Setup (Cursor GitHub MCP)

Enable MCP permissions for:

- Repository reads
- Issue creation
- Pull-request creation and comments
- CI status inspection

Do **not** enable automatic merges or releases yet.

## Agent behavior

When authenticated, the First Mate should create real issues/PRs after an approved implementation.

When not authenticated, use:

- Local issue placeholder (`local/<slug>`)
- PR-ready description in the completion report

See Skill: `.cursor/skills/github-integration/SKILL.md`.


## Verified

- Account: `loganware05`
- Date: 2026-07-10
- Scopes: `repo`, `workflow`, `read:org`, `gist`
