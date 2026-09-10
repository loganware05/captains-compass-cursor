#!/usr/bin/env bash
# example-design-repo-scorecard.sh — Starred design-repo TI scorecard path (M23).
# categorize → security/supply-chain gate → usefulness labels → draft proposal.
# Never auto-installs Skills; approved_for_execution stays false; no clone/exec.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-$ROOT}"
OBJECTIVE="${OBJECTIVE:-design system craft tokens ui primitives}"
CATEGORY_FILTER="${CATEGORY_FILTER:-design-system}"
TOP_N="${TOP_N:-1}"

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$REPO_ROOT" "$OBJECTIVE" "$CATEGORY_FILTER" "$TOP_N" "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.learning.drafts import write_unified_skill_draft
from orchestrator.learning.export import export_categorized_to_staging
from orchestrator.learning.scorecard import write_ti_scorecard_evidence
from orchestrator.providers.technology_intelligence.github_stars_provider import (
    load_recorded_starred_fixtures,
)
from orchestrator.providers.technology_intelligence.stars_categorization import (
    run_batch_categorization,
)

repo_root = Path(sys.argv[1]).resolve()
objective = sys.argv[2]
category = sys.argv[3] or None
top_n = int(sys.argv[4])
control = Path(sys.argv[5]).resolve()

fixtures = control / "tests" / "fixtures" / "ti" / "github-stars-recorded"
labels = control / "tests" / "fixtures" / "ti" / "github-stars-labels" / "manual-labels.json"
repos = load_recorded_starred_fixtures(fixtures)
cat = run_batch_categorization(
    repo_root,
    repos,
    labels_path=labels,
    source="fixtures:github-stars-recorded",
)
exported = export_categorized_to_staging(
    repo_root,
    objective,
    top_n=top_n,
    category_filter=category or None,
)
results = []
for item in exported:
    scorecard = write_ti_scorecard_evidence(
        repo_root,
        repo=item["repo"],
        candidate=item["candidate"],
        category=str(item.get("star_category") or ""),
    )
    candidate = dict(item["candidate"])
    candidate["evidence_paths"] = scorecard["evidence_paths"]
    candidate["approved_for_execution"] = False
    drafts = write_unified_skill_draft(
        repo_root,
        candidate,
        item["skill_slug"],
        "ANALYZED",
        evidence_paths=scorecard["evidence_paths"],
    )
    results.append(
        {
            "full_name": item["full_name"],
            "star_category": item["star_category"],
            "staging_path": item["staging_path"],
            "scorecard_path": scorecard["scorecard_path"],
            "evidence_paths": scorecard["evidence_paths"],
            "draft_skill_md": str(drafts["skill_md"]),
            "approved_for_execution": False,
            "auto_install": False,
            "clone_or_exec": False,
        }
    )

out = {
    "kind": "m23-design-repo-scorecard-example",
    "categorization": cat,
    "objective": objective,
    "category_filter": category,
    "approved_for_execution": False,
    "auto_install": False,
    "results": results,
    "notes": (
        "Example path only. No live Skill install. Captain must approve any "
        "promotion via promote-candidate.sh --captain-approved."
    ),
}
out_dir = repo_root / ".agent" / "evidence" / "m23-ti-skill-flywheel"
out_dir.mkdir(parents=True, exist_ok=True)
path = out_dir / "example-design-repo-scorecard.json"
path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"report_path": str(path), **{k: out[k] for k in ("approved_for_execution", "auto_install")}}, indent=2))
print(json.dumps(out, indent=2))
PY
