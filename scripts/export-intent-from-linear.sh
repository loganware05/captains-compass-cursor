#!/usr/bin/env bash
# Export a draft intent pack from Linear issue fields (read-only).
# Never sets captain_approval — Linear is a flight recorder, not an approver.
set -euo pipefail

OUT=""
FIXTURE=""
ISSUE_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --fixture) FIXTURE="$2"; shift 2 ;;
    --issue) ISSUE_ID="$2"; shift 2 ;;
    -h|--help)
      cat <<'EOF'
Usage: export-intent-from-linear.sh --out PATH [--fixture PATH | --issue ID]

Build a draft intent pack JSON from Linear-shaped fields.
Always writes captain_approval: false.

Options:
  --out PATH       Output intent pack JSON path (required)
  --fixture PATH   Local JSON fixture with Linear-like fields (preferred for CI)
  --issue ID       Live Linear issue id (requires LINEAR_API_KEY; optional)
  -h, --help       Show this help
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$OUT" ]]; then
  echo "--out is required" >&2
  exit 2
fi

if [[ -n "$ISSUE_ID" && -z "${LINEAR_API_KEY:-}" && -z "$FIXTURE" ]]; then
  echo "Live Linear export requires LINEAR_API_KEY or --fixture" >&2
  exit 2
fi

python3 - "$OUT" "${FIXTURE:-}" "${ISSUE_ID:-}" <<'PY'
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
fixture = sys.argv[2] or None
issue_id = sys.argv[3] or None

source = {
    "title": "",
    "status": "",
    "acceptance_criteria": [],
    "non_goals": [],
    "rollback": [],
    "security_notes": [],
    "domains": [],
    "excerpt": "",
    "linear_issue_id": issue_id or "",
    "plan_path": "",
}

if fixture:
    data = json.loads(Path(fixture).read_text(encoding="utf-8"))
    for key in source:
        if key in data and data[key] is not None:
            source[key] = data[key]
    if "id" in data and not source["linear_issue_id"]:
        source["linear_issue_id"] = str(data["id"])
    if "description" in data and not source["excerpt"]:
        source["excerpt"] = str(data["description"])
    if "summary" in data and not source["excerpt"]:
        source["excerpt"] = str(data["summary"])
elif issue_id:
    # Live API is optional; without a fixture we only stamp the issue id.
    source["title"] = f"Linear issue {issue_id}"
    source["excerpt"] = (
        "Draft intent exported from Linear issue id only. "
        "Replace with full issue fields via --fixture for CI-safe runs."
    )

pack = {
    "schema_version": "northstar.intent_pack.v1",
    "source": "linear" if (fixture or issue_id) else "fixture",
    "plan_path": source.get("plan_path") or "",
    "linear_issue_id": source.get("linear_issue_id") or "",
    "title": source.get("title") or "Untitled intent",
    "status": source.get("status") or "",
    "acceptance_criteria": list(source.get("acceptance_criteria") or []),
    "non_goals": list(source.get("non_goals") or []),
    "rollback": list(source.get("rollback") or []),
    "security_notes": list(source.get("security_notes") or []),
    "domains": list(source.get("domains") or []),
    "excerpt": source.get("excerpt") or "",
    "captain_approval": False,
}

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
print(f"Wrote draft intent pack (captain_approval=false): {out}")
PY
