#!/usr/bin/env bash
# uninstall.sh — Remove Captain's Compass workflow package from a product repo.
# Does NOT delete product memory docs (PROJECT_CONTEXT.md, etc.) by default.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: uninstall.sh --yes <target-repo-path>

Removes .cursor rules/skills/agents/hooks installed by Captain's Compass and
.agent/COMPASS_VERSION. Product docs (AGENTS.md, PROJECT_CONTEXT.md, ...) are
kept unless --purge-docs is also passed.

Requires --yes to proceed.

Example:
  ./scripts/uninstall.sh --yes ~/Projects/my-app
USAGE
}

YES=0
PURGE_DOCS=0
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) YES=1; shift ;;
    --purge-docs) PURGE_DOCS=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      TARGET="$1"; shift ;;
  esac
done

if [[ "$YES" -ne 1 || -z "$TARGET" ]]; then
  usage >&2
  exit 1
fi

TARGET="$(cd "$TARGET" && pwd)"

if [[ ! -d "$TARGET/.git" ]]; then
  echo "error: not a git repository: $TARGET" >&2
  exit 1
fi

echo "Uninstalling Captain's Compass from $TARGET"

rm -rf \
  "$TARGET/.cursor/rules" \
  "$TARGET/.cursor/skills" \
  "$TARGET/.cursor/agents" \
  "$TARGET/.cursor/hooks" \
  "$TARGET/.cursor/hooks.json" \
  "$TARGET/.cursor/commands"

rm -f "$TARGET/.agent/COMPASS_VERSION"

if [[ "$PURGE_DOCS" -eq 1 ]]; then
  echo "Purging product memory docs (--purge-docs)"
  rm -f \
    "$TARGET/AGENTS.md" \
    "$TARGET/PROJECT_CONTEXT.md" \
    "$TARGET/IMPLEMENTATION_PLAN.md" \
    "$TARGET/DECISIONS.md" \
    "$TARGET/PROGRESS.md" \
    "$TARGET/TESTING.md" \
    "$TARGET/CHANGELOG.md"
fi

# Clean empty .cursor if vacant
if [[ -d "$TARGET/.cursor" ]] && [[ -z "$(ls -A "$TARGET/.cursor" 2>/dev/null || true)" ]]; then
  rmdir "$TARGET/.cursor" 2>/dev/null || true
fi

echo "Uninstall complete. Product source code was not modified."
