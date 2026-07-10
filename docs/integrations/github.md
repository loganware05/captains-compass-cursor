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

## Live repositories

| Repo | URL | Visibility |
|---|---|---|
| Control (workflow) | https://github.com/loganware05/captains-compass-cursor | Private |
| Sandbox (validation) | https://github.com/loganware05/captain-compass-sandbox | Private |

## Enable as GitHub template (manual)

On the control repository:

1. Open **Settings**
2. Enable **Template repository**
3. Topics already applied: `cursor`, `agentic-engineering`, `ai-agents`, `developer-workflow`, `git-worktrees`
4. Optional: create a GitHub Release for `v0.2.0`

```bash
cd /path/to/captains-compass-cursor
git tag -a v0.2.0 -m "Captain's Compass v0.2.0"
git push origin v0.2.0
gh release create v0.2.0 --title "v0.2.0" --notes-file CHANGELOG.md
```
