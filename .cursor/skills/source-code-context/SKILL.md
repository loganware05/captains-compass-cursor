---
name: source-code-context
description: Fetches and searches real package or repo source (prefer opensrc) before guessing APIs from incomplete docs
---

# Source Code as Agent Context

## Use this Skill when

Integrating or debugging a package, SDK, framework, or open-source tool when docs are weak, stale, or incomplete—or when the agent is guessing API names that may not exist.

## Inputs

- Package or repository name (and version if known)
- Product repo lockfiles / dependency manifests when present
- Optional: Captain-approved local reference path under `reference/repos/`

## Prerequisites

**Preferred (optional):** [opensrc](https://github.com/vercel-labs/opensrc) CLI for fetch-and-cache of dependency source.

```bash
npm install -g opensrc
command -v opensrc   # must succeed before relying on opensrc path
```

See `docs/integrations/opensrc.md` in the control repo (or the installed product copy of that doc if present).

`opensrc` is **not** required for Compass install or doctor. If unavailable, use the fallback path below.

## Procedure

1. Confirm the task needs implementation detail beyond types/docs (internal behavior, edge cases, current API shape).
2. Prefer **opensrc** when installed:
   - `opensrc path <package>` (npm; lockfile version via `--cwd` when useful)
   - `opensrc path pypi:<package>` / `opensrc path crates:<crate>` / `opensrc path owner/repo`
   - Search with `rg`, `find`, or read specific files under the returned path
3. If opensrc is unavailable, use a **Captain-approved** local checkout, e.g. `reference/repos/github.com/<org>/<repo>`, or an existing clone path the Captain provides. Do not invent large reference trees without approval.
4. Identify the concrete files/functions/examples used as reference.
5. Implement only the minimal product change needed.
6. In the summary, cite which source paths were searched and which symbols were followed.
7. If the API still cannot be found, stop and report—do **not** silently install a replacement package.

## Output

Working change (under an approved plan when product behavior changes), plus a short citation of the source files/symbols referenced.

## Prohibited actions

- Guessing API names when package/repo source is available to search
- Dumping entire repositories into chat context
- Installing alternative dependencies without Captain approval
- Treating opensrc as mandatory (fallback must remain valid)
- Fetching source for trivial questions that types or official docs already answer
