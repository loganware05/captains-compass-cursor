# Product Repository Onboarding

Install Captain's Compass into a **product** repository after validating the workflow in a disposable sandbox.

Control repository: https://github.com/loganware05/captains-compass-cursor  
Current stable version: **1.1.0**

Do not install into critical production repos until sandbox validation has passed. See [`SANDBOX_VALIDATION.md`](SANDBOX_VALIDATION.md).

## Prerequisites

- Git and Bash
- A local clone of this control repository (or a release checkout)
- Cursor IDE for day-to-day agent work
- Optional: authenticated `gh` for issues and pull requests

```bash
# From the control repo
./scripts/doctor.sh
```

## Path A — New project

Generate or create the product repository first, then install Compass.

```bash
git clone git@github.com:<org>/<new-project>.git
cd <new-project>

# Optional: start on an install branch before the first merge
git checkout -b chore/install-captains-compass

/path/to/captains-compass-cursor/scripts/install.sh "$(pwd)"

git add .
git commit -m "chore(workflow): install Captain's Compass"
git push -u origin chore/install-captains-compass
# Open a PR, review, and merge
```

After merge:

1. Open the repository alone in Cursor.
2. Paste **Prompt 2** from [`AGENT_INSTALL_PROMPT.md`](AGENT_INSTALL_PROMPT.md) so the First Mate interviews you and fills `PROJECT_CONTEXT.md`.
3. Ask the First Mate to follow `AGENTS.md` for the next change.
4. Expect `IMPLEMENTATION_PLAN.md` to reach **AWAITING APPROVAL** before product code changes.

## Path B — Existing project

Always install through a dedicated branch and pull request.

```bash
cd existing-project
git checkout -b chore/install-captains-compass

/path/to/captains-compass-cursor/scripts/install.sh "$(pwd)"

git add .
git commit -m "chore(workflow): install Captain's Compass"
git push -u origin chore/install-captains-compass
```

Review the PR carefully:

- `.cursor/` rules, Skills, agents, hooks
- Root memory templates (`AGENTS.md`, `PROJECT_CONTEXT.md`, …) — only created if missing
- `.agent/COMPASS_VERSION` and `.agent/evidence/`

Merge only after the Captain is satisfied.

## Update an existing install

From the control repo (does **not** overwrite existing product memory docs):

```bash
/path/to/captains-compass-cursor/scripts/update.sh /path/to/product-repo
```

Details: [`UPGRADING.md`](UPGRADING.md).

## Uninstall

Removes Compass control files; preserves product memory docs by default:

```bash
/path/to/captains-compass-cursor/scripts/uninstall.sh --yes /path/to/product-repo
```

## Verify

```bash
/path/to/captains-compass-cursor/scripts/doctor.sh /path/to/product-repo
```

Doctor reads `.agent/COMPASS_VERSION` in product repos (there is no product `VERSION` file).

## What gets installed

| Asset | Behavior on re-install / update |
|---|---|
| `.cursor/rules`, `skills`, `agents`, hooks | Refreshed |
| Doc templates at repo root | Created if missing; **not** overwritten |
| `.agent/COMPASS_VERSION` | Updated to the control-repo version |
| Control-repo `scripts/` | **Not** copied into the product repo — run them from the control repo |

## Next steps after install

1. Customize `PROJECT_CONTEXT.md`, `TESTING.md`, and `DECISIONS.md`.
2. Use the approval gate for every product-behavior change.
3. Store evidence under `.agent/evidence/` before opening PRs (PR evidence hook).

### Agent-ready prompts

For copy-paste Cursor agent instructions (install + activate / fill `PROJECT_CONTEXT.md`), see [`AGENT_INSTALL_PROMPT.md`](AGENT_INSTALL_PROMPT.md).

Recommended sequence: install (Prompt 1) → open the product repo alone → activate with Prompt 2 so the First Mate interviews the Captain and fills project memory before the first feature plan.
