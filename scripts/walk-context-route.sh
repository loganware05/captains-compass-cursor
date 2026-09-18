#!/usr/bin/env bash
# walk-context-route.sh — Resolve a context route segment-by-segment (M40)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: walk-context-route.sh [--repo-root PATH] --route domain/module [--context-root DIR]

Sequentially resolves a context route against the derived .agent/context/ tree
and prints the route result (steps + in-scope inode refs) as JSON. Loads only
the nodes on the walked path; returns inode pointers, never source content.

Options:
  --repo-root PATH     Repository to walk (default: control repo root)
  --route PATH         Context route, e.g. orchestrator/review (required)
  --context-root DIR   Context tree root (default: <repo>/.agent/context)
  -h, --help           Show help
USAGE
}

REPO_ROOT="$ROOT"
ROUTE=""
CONTEXT_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="${2:-}"
      shift 2
      ;;
    --route)
      ROUTE="${2:-}"
      shift 2
      ;;
    --context-root)
      CONTEXT_ROOT="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$ROUTE" ]]; then
  echo "error: --route is required" >&2
  usage >&2
  exit 1
fi

PYTHONPATH="$ROOT" python3 - "$REPO_ROOT" "$ROUTE" "$CONTEXT_ROOT" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.context.walker import walk_route

repo_root = Path(sys.argv[1]).resolve()
route = sys.argv[2]
context_root = Path(sys.argv[3]).resolve() if sys.argv[3] else None

result = walk_route(repo_root, route, context_root=context_root)
print(json.dumps(result, indent=2))
sys.exit(0 if result["resolved"] else 1)
PY
