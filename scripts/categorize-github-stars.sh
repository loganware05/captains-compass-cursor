#!/usr/bin/env bash
# categorize-github-stars.sh — Offline batch ML categorization for starred repos (M14).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
SOURCE="ti-cache"
LIMIT=100

usage() {
  cat <<'USAGE'
Usage: categorize-github-stars.sh [--repo-root PATH] [--source ti-cache|live|fixtures]

Train from manual label fixtures and write
.agent/ti/github-stars-categorized/categorized.json.

Sources:
  ti-cache   Read .agent/intelligence/ti-cache/starred-repos.json (default)
  live       Fetch via authenticated gh (Captain local only)
  fixtures   Use tests/fixtures/ti/github-stars-recorded (offline)

Explicit CLI only — never auto-runs on workstream close.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$SOURCE" "$LIMIT" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.providers.technology_intelligence.github_stars_provider import (
    fetch_starred_repos,
    load_recorded_starred_fixtures,
)
from orchestrator.providers.technology_intelligence.stars_categorization import run_batch_categorization
from orchestrator.providers.technology_intelligence.ti_cache import read_ti_cache

repo = Path(sys.argv[1]).resolve()
source = sys.argv[2].strip().lower() or "ti-cache"
limit = int(sys.argv[3])

if source == "fixtures":
    fixtures = repo / "tests" / "fixtures" / "ti" / "github-stars-recorded"
    repos = load_recorded_starred_fixtures(fixtures)
    src_label = "fixtures:github-stars-recorded"
elif source == "live":
    repos = fetch_starred_repos(limit=limit)
    if not repos:
        print(json.dumps({"error": "gh unavailable or not authenticated"}, indent=2))
        raise SystemExit(1)
    src_label = "gh api user/starred"
else:
    repos = read_ti_cache(repo)
    if not repos:
        print(json.dumps({"error": "ti-cache empty; run refresh-ti-cache.sh first"}, indent=2))
        raise SystemExit(1)
    src_label = "ti-cache:starred-repos.json"

report = run_batch_categorization(repo, repos, source=src_label)
print(json.dumps(report, indent=2))
PY
