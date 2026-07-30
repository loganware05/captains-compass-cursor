# Captain's Compass Cursor

Reusable **Cursor IDE** agentic engineering workflow template.

**GitHub template:** https://github.com/loganware05/captains-compass-cursor

This is a **control repository**. It owns rules, Skills, subagents, hooks, document templates, and scripts. Product application code does not live here.

## Current version: 1.1.0

### Included

- Approval-gated operating model (`AGENTS.md` + five core rules)
- Twenty Skills (foundational + tech/integration + source-context, cleanup, review-fix loop)
- Eight specialist subagents
- Seven safety hooks
- `install.sh`, `update.sh`, `uninstall.sh`, `doctor.sh`
- Documentation templates and integration guides
- Automated installer / doctor / hook tests

### Operating model

- **Captain** — human owner; approves plans and merges
- **First Mate** — coordinating Cursor agent
- **Approval gate** — no product implementation changes until `IMPLEMENTATION_PLAN.md` is **APPROVED**

## Quick start (control repo)

```bash
./scripts/doctor.sh
./tests/run.sh
```

## Install into a product repository

Full guide (new vs existing projects): [`docs/PRODUCT_ONBOARDING.md`](docs/PRODUCT_ONBOARDING.md).

Copy-paste Cursor agent prompts (install + activate / fill `PROJECT_CONTEXT.md`): [`docs/AGENT_INSTALL_PROMPT.md`](docs/AGENT_INSTALL_PROMPT.md).

```bash
./scripts/install.sh /path/to/product-repo
```

## Update an existing install

The version in the **control-repo checkout** determines what gets installed.
First inspect the product repo's current version, then choose a newer release:

```bash
CONTROL="/absolute/path/to/captains-compass-cursor"
PRODUCT="/absolute/path/to/product-repo"

CURRENT_VERSION="v$(tr -d '[:space:]' < "$PRODUCT/.agent/COMPASS_VERSION")"
git -C "$CONTROL" fetch origin --tags || exit 1

# Latest valid version tag, or replace with an explicit newer tag (for example vX.Y.Z).
TARGET_VERSION="$(git -C "$CONTROL" tag --list 'v*' --sort=-version:refname | awk '/^v[0-9]+\.[0-9]+\.[0-9]+$/ { print; exit }')"
STABLE_SEMVER='^v[0-9]+\.[0-9]+\.[0-9]+$'
[[ "$CURRENT_VERSION" =~ $STABLE_SEMVER && "$TARGET_VERSION" =~ $STABLE_SEMVER ]] || {
  printf 'Invalid stable version: current=%s target=%s\n' "$CURRENT_VERSION" "$TARGET_VERSION" >&2
  exit 1
}
LOCAL_COMMIT="$(git -C "$CONTROL" rev-parse --verify "refs/tags/${TARGET_VERSION}^{commit}")"
REMOTE_COMMIT="$(
  git -C "$CONTROL" ls-remote --tags origin \
    "refs/tags/$TARGET_VERSION" "refs/tags/$TARGET_VERSION^{}" |
    awk '$2 ~ /\^\{\}$/ { peeled=$1 } $2 !~ /\^\{\}$/ { direct=$1 }
      END { print peeled ? peeled : direct }'
)"
[[ -n "$REMOTE_COMMIT" && "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]] || {
  printf 'Local/remote tag mismatch for %s\n' "$TARGET_VERSION" >&2
  exit 1
}

semver_gt() {
  local target="${1#v}" current="${2#v}"
  local t_major t_minor t_patch c_major c_minor c_patch
  IFS=. read -r t_major t_minor t_patch <<< "$target"
  IFS=. read -r c_major c_minor c_patch <<< "$current"
  (( 10#$t_major > 10#$c_major ||
    (10#$t_major == 10#$c_major && 10#$t_minor > 10#$c_minor) ||
    (10#$t_major == 10#$c_major && 10#$t_minor == 10#$c_minor &&
      10#$t_patch > 10#$c_patch) ))
}
semver_gt "$TARGET_VERSION" "$CURRENT_VERSION" || {
  printf 'Refusing non-forward update: %s -> %s\n' "$CURRENT_VERSION" "$TARGET_VERSION" >&2
  exit 1
}
```

Run the selected release from a temporary detached worktree so your normal
control-repo checkout is not changed:

```bash
(
  set -euo pipefail
  UPDATE_WORKTREE="$(mktemp -d "${TMPDIR:-/tmp}/captains-compass-update-XXXXXX")"
  cleanup_update_worktree() {
    git -C "$CONTROL" worktree remove "$UPDATE_WORKTREE" 2>/dev/null || true
    rmdir "$UPDATE_WORKTREE" 2>/dev/null || true
  }
  trap cleanup_update_worktree EXIT

  git -C "$CONTROL" worktree add --detach "$UPDATE_WORKTREE" "$TARGET_VERSION"
  git -C "$PRODUCT" switch -c "chore/update-captains-compass-${TARGET_VERSION}"
  "$UPDATE_WORKTREE/scripts/update.sh" "$PRODUCT"
  "$UPDATE_WORKTREE/scripts/doctor.sh" "$PRODUCT"
)

git -C "$PRODUCT" status --short
git -C "$PRODUCT" add .cursor .agent/COMPASS_VERSION .cursorignore .gitignore
git -C "$PRODUCT" diff --cached
```

Review the release notes before updating, then commit the product-repo workflow
changes and open a PR. Filled-in product memory docs are preserved.

`update.sh` supports **forward upgrades only**. Downgrades can leave workflow
files introduced by newer versions and are not supported.

See [`docs/UPGRADING.md`](docs/UPGRADING.md) for safeguards, pinned-version
instructions, validation, and troubleshooting.

## Uninstall

```bash
./scripts/uninstall.sh --yes /path/to/product-repo
```

## Integrations

| Area | Doc |
|---|---|
| GitHub | [`docs/integrations/github.md`](docs/integrations/github.md) |
| Node / Postgres / Prisma | [`docs/integrations/node-postgres-prisma.md`](docs/integrations/node-postgres-prisma.md) |
| Docker / cloud | [`docs/integrations/docker-cloud.md`](docs/integrations/docker-cloud.md) / [`cloud-mcp.md`](docs/integrations/cloud-mcp.md) |
| Linear / Notion | [`linear.md`](docs/integrations/linear.md) / [`notion.md`](docs/integrations/notion.md) |
| Python / ML | [`docs/integrations/python-ml.md`](docs/integrations/python-ml.md) |
| iOS | [`docs/integrations/ios.md`](docs/integrations/ios.md) |
| opensrc (optional) | [`docs/integrations/opensrc.md`](docs/integrations/opensrc.md) |
| Postgres MCP | [`docs/integrations/postgres-mcp.md`](docs/integrations/postgres-mcp.md) |

## Releases

See [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) and [`CHANGELOG.md`](CHANGELOG.md).

## License

See [LICENSE](LICENSE).
