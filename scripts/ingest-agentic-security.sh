#!/usr/bin/env bash
# ingest-agentic-security.sh — Opt-in Cursor Agentic Security Review ingest (M39).
# Never runs on the default northstar review path. Refuse-closed without allowlist.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT=""
ARTIFACT=""
GITHUB_REPO=""
RUN_ID=""
ALLOWLIST=""
OUTCOMES_PROPOSAL=0

usage() {
  cat <<'USAGE'
Usage: ingest-agentic-security.sh --repo-root PATH --artifact PATH --github-repo OWNER/NAME [options]

Options:
  --repo-root PATH         Repository receiving evidence (required)
  --artifact PATH          Exported Cursor Security Review JSON (required)
  --github-repo OWNER/NAME Repo slug for allowlist gate (required)
  --run-id ID              Evidence run id (default: generated)
  --allowlist PATH         Allowlist YAML/JSON (default: .agent/review/agentic-security-allowlist.yml)
  --outcomes-proposal      Attach proposal-only M31 outcome stubs
  -h, --help               Show help

Locks:
  Default northstar review is unchanged (hermetic specialists).
  Ingest is refuse-closed when allowlist.enabled=false or repo missing.
  Never auto-merges / never invokes Cursor Cloud from this script.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --artifact) ARTIFACT="$2"; shift 2 ;;
    --github-repo) GITHUB_REPO="$2"; shift 2 ;;
    --run-id) RUN_ID="$2"; shift 2 ;;
    --allowlist) ALLOWLIST="$2"; shift 2 ;;
    --outcomes-proposal) OUTCOMES_PROPOSAL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$REPO_ROOT" || -z "$ARTIFACT" || -z "$GITHUB_REPO" ]]; then
  echo "error: --repo-root, --artifact, and --github-repo are required" >&2
  usage >&2
  exit 2
fi

export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$ARTIFACT" "$GITHUB_REPO" "$RUN_ID" "$ALLOWLIST" "$OUTCOMES_PROPOSAL" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root))

from orchestrator.review.agentic_security_ingest import (
    AgenticSecurityIngestError,
    ingest_agentic_security,
)

repo_root = Path(sys.argv[2])
artifact = Path(sys.argv[3])
slug = sys.argv[4]
run_id = sys.argv[5] or None
allowlist = Path(sys.argv[6]) if sys.argv[6] else None
outcomes = sys.argv[7] == "1"

try:
    report = ingest_agentic_security(
        repo_root=repo_root,
        artifact_path=artifact,
        repo_slug=slug,
        run_id=run_id or None,
        allowlist_path=allowlist,
        outcomes_proposal=outcomes,
    )
except AgenticSecurityIngestError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

rid = report["run_id"]
out = repo_root / ".agent" / "evidence" / "review" / rid / "agentic-security"
print(f"ingested {report['finding_count']} finding(s) → {out}")
PY
