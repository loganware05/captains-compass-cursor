# opensrc (optional)

[opensrc](https://github.com/vercel-labs/opensrc) fetches and caches package/repo source so agents can search real implementations instead of guessing from incomplete docs.

Captain's Compass treats opensrc as **preferred-optional** tooling for the `source-code-context` Skill. It is **not** required for Compass install, update, uninstall, or doctor.

## Install

```bash
npm install -g opensrc
command -v opensrc
```

Requires a working Node/npm toolchain for the global install. The CLI itself is a native binary.

## Common usage

```bash
# npm package (prefers lockfile version when --cwd points at the product repo)
rg "parse" $(opensrc path zod --cwd /path/to/product-repo)
cat $(opensrc path zod)/src/types.ts

# Other registries
opensrc path pypi:requests
opensrc path crates:serde
opensrc path vercel/next.js

# Prefetch without printing a path
opensrc fetch zod react
opensrc list
```

Cache location: `~/.opensrc/` (override with `OPENSRC_HOME`).

## When agents should use it

- Understanding internal library behavior beyond types
- Verifying current API shapes for a dependency the product already uses
- Learning patterns from a well-known implementation

Do **not** fetch source for simple API questions that official docs or local types already answer.

## Fallback without opensrc

Use a Captain-approved local checkout, for example:

```text
reference/repos/github.com/<org>/<repo>
```

Point the agent at that path and require it to cite files searched. Avoid committing large reference trees unless the Captain explicitly wants them in the product repo.

## Compass rules

- Prefer evidence over guesses (`source-code-context` Skill)
- Do not silently swap dependencies when an API is hard to find
- Product-behavior changes still require an approved `IMPLEMENTATION_PLAN.md`
