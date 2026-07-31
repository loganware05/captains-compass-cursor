#!/usr/bin/env bash
# install.sh — Install Captain's Compass workflow package into a product Git repository.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: install.sh [--force] <target-repo-path>

Copies Captain's Compass rules, Skills, agents, and documentation templates
into a product Git repository.

Options:
  --force   Overwrite existing workflow files
  -h, --help  Show this help

Example:
  ./scripts/install.sh ~/Projects/my-app
USAGE
}

FORCE=0
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      if [[ -n "$TARGET" ]]; then
        echo "error: unexpected argument: $1" >&2
        usage >&2
        exit 1
      fi
      TARGET="$1"
      shift
      ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "error: target repository path is required" >&2
  usage >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$(cd "$TARGET" && pwd)"

if [[ ! -d "$TARGET/.git" ]]; then
  echo "error: target is not a Git repository: $TARGET" >&2
  exit 1
fi

if [[ "$TARGET" == "$SOURCE_ROOT" ]]; then
  echo "error: refusing to install into the Captain's Compass control repository itself" >&2
  exit 1
fi

VERSION="$(tr -d '[:space:]' < "$SOURCE_ROOT/VERSION")"

DOC_FILES=(
  AGENTS.md
  PROJECT_CONTEXT.md
  IMPLEMENTATION_PLAN.md
  DECISIONS.md
  PROGRESS.md
  TESTING.md
  CHANGELOG.md
)

conflicts=()

check_conflict() {
  local path="$1"
  if [[ -e "$TARGET/$path" ]]; then
    conflicts+=("$path")
  fi
}

# Detect conflicts for top-level docs and .cursor package dirs
for f in "${DOC_FILES[@]}"; do
  check_conflict "$f"
done
check_conflict ".cursor/rules"
check_conflict ".cursor/skills"
check_conflict ".cursor/agents"
check_conflict ".cursor/hooks"
check_conflict ".cursor/hooks.json"

if [[ ${#conflicts[@]} -gt 0 && "$FORCE" -ne 1 ]]; then
  echo "error: refusing to overwrite existing workflow files (pass --force to overwrite):" >&2
  for c in "${conflicts[@]}"; do
    echo "  - $c" >&2
  done
  exit 1
fi

mkdir -p "$TARGET/.cursor" "$TARGET/.agent/evidence" "$TARGET/.agent/budgets" "$TARGET/.agent/budgets/_templates" "$TARGET/.agent/budgets/private"

# Copy Cursor package
cp -R "$SOURCE_ROOT/.cursor/rules" "$TARGET/.cursor/"
cp -R "$SOURCE_ROOT/.cursor/skills" "$TARGET/.cursor/"
cp -R "$SOURCE_ROOT/.cursor/agents" "$TARGET/.cursor/"

# Hooks (scripts + hooks.json)
if [[ -d "$SOURCE_ROOT/.cursor/hooks" ]]; then
  mkdir -p "$TARGET/.cursor/hooks"
  cp -R "$SOURCE_ROOT/.cursor/hooks/." "$TARGET/.cursor/hooks/"
  chmod +x "$TARGET/.cursor/hooks/"*.sh 2>/dev/null || true
fi
if [[ -f "$SOURCE_ROOT/.cursor/hooks.json" ]]; then
  cp "$SOURCE_ROOT/.cursor/hooks.json" "$TARGET/.cursor/hooks.json"
fi
if [[ -d "$SOURCE_ROOT/.cursor/commands" ]]; then
  mkdir -p "$TARGET/.cursor/commands"
  cp -R "$SOURCE_ROOT/.cursor/commands/." "$TARGET/.cursor/commands/"
fi

# Copy documentation templates only when missing (never clobber product memory on --force)
for f in "${DOC_FILES[@]}"; do
  if [[ -f "$TARGET/$f" ]]; then
    echo "keep: $f (already exists; not overwritten)"
  else
    cp "$SOURCE_ROOT/templates/docs/$f" "$TARGET/$f"
    echo "added: $f"
  fi
done

# Thin Claude Code adapter — only when missing (never overwrite customized CLAUDE.md)
if [[ -f "$SOURCE_ROOT/templates/docs/CLAUDE.md" ]]; then
  if [[ -f "$TARGET/CLAUDE.md" ]]; then
    echo "keep: CLAUDE.md (already exists; not overwritten)"
  else
    cp "$SOURCE_ROOT/templates/docs/CLAUDE.md" "$TARGET/CLAUDE.md"
    echo "added: CLAUDE.md"
  fi
fi

# Optional guidance docs (install when missing; do not clobber)
mkdir -p "$TARGET/docs"
for f in EVIDENCE_MATRIX.md; do
  if [[ -f "$SOURCE_ROOT/docs/$f" ]]; then
    if [[ -f "$TARGET/docs/$f" ]]; then
      echo "keep: docs/$f (already exists; not overwritten)"
    else
      cp "$SOURCE_ROOT/docs/$f" "$TARGET/docs/$f"
      echo "added: docs/$f"
    fi
  fi
done
if [[ -f "$SOURCE_ROOT/docs/integrations/multi-runtime-agents.md" ]]; then
  mkdir -p "$TARGET/docs/integrations"
  if [[ -f "$TARGET/docs/integrations/multi-runtime-agents.md" ]]; then
    echo "keep: docs/integrations/multi-runtime-agents.md (already exists; not overwritten)"
  else
    cp "$SOURCE_ROOT/docs/integrations/multi-runtime-agents.md" "$TARGET/docs/integrations/multi-runtime-agents.md"
    echo "added: docs/integrations/multi-runtime-agents.md"
  fi
fi

# Budget templates (refreshable; live ledgers under .agent/budgets/ are product-owned)
if [[ -d "$SOURCE_ROOT/templates/agent" ]]; then
  mkdir -p "$TARGET/.agent/budgets/_templates"
  cp "$SOURCE_ROOT/templates/agent/"*.md "$TARGET/.agent/budgets/_templates/" 2>/dev/null || true
fi

# Copy ignore helpers if missing
if [[ ! -f "$TARGET/.cursorignore" ]]; then
  cp "$SOURCE_ROOT/.cursorignore" "$TARGET/.cursorignore"
fi

# Ensure .gitignore has agent evidence entries
GITIGNORE="$TARGET/.gitignore"
touch "$GITIGNORE"
ensure_gitignore_line() {
  local line="$1"
  if ! grep -qxF "$line" "$GITIGNORE" 2>/dev/null; then
    echo "$line" >> "$GITIGNORE"
  fi
}

if ! grep -q "Captain's Compass" "$GITIGNORE" 2>/dev/null; then
  {
    echo ""
    echo "# Captain's Compass"
    echo ".agent/evidence/private/"
    echo ".agent/budgets/private/"
    echo ".agent/runs/"
    echo ".env"
    echo ".env.*"
    echo "!.env.example"
  } >> "$GITIGNORE"
else
  ensure_gitignore_line ".agent/evidence/private/"
  ensure_gitignore_line ".agent/budgets/private/"
  ensure_gitignore_line ".agent/runs/"
fi

# Record installed version
mkdir -p "$TARGET/.agent"
echo "$VERSION" > "$TARGET/.agent/COMPASS_VERSION"

cat <<EOF

Captain's Compass v${VERSION} installed into:
  $TARGET

Next steps:
  1. Fill in PROJECT_CONTEXT.md for this product.
  2. Open the repository in Cursor.
  3. Ask the First Mate to follow AGENTS.md for your next change.
  4. Expect IMPLEMENTATION_PLAN.md to reach AWAITING APPROVAL before product code changes.

Do not install into critical production repos until you have validated the workflow in a disposable sandbox.

Note: --force refreshes .cursor rules/skills/agents/hooks but does not overwrite existing
product memory docs (PROJECT_CONTEXT.md, IMPLEMENTATION_PLAN.md, etc.).
EOF
