# Code review report — `control-m27-fixture`

- Repository: `/agent/repos/captains-compass-cursor`
- Status: **completed**
- Created: 2026-09-12T20:55:05Z
- Domains: python, security
- Findings: 3 (verified=1, unverified=1, discarded=1)
- GitHub review posted: `False`

## Findings

### sec-hardcoded-key: Hardcoded API key introduced in session helper

- Severity: `high`
- Confidence: `0.93`
- Status: **verified**
- Skill: `security-review`
- Evidence: `src/auth/session.py`

New assignment writes a live-looking API key into session payload.

**Suggested fix:** Remove hardcoded secret; load from environment; rotate if exposed.

### intent-ac-check: Confirm acceptance criteria still covered

- Severity: `medium`
- Confidence: `0.66`
- Status: **unverified**
- Skill: `code-reviewer`
- Evidence: `IMPLEMENTATION_PLAN.md`, `src/auth/session.py`

Plan lists evidence-only reviews; ensure no GitHub posting was added.

**Suggested fix:** Keep GitHub posting out of MVP; document evidence path.

### noise-naming: Variable rename preference

- Severity: `low`
- Confidence: `0.2`
- Status: **discarded**
- Skill: `code-reviewer`
- Evidence: _none_

Style-only preference without behavioral impact.

_Discard reason:_ `missing_evidence_paths`

## Provenance

```json
{
  "candidates_source": "fixtures",
  "github_review_posted": false,
  "hermetic": true,
  "invoke_model": false,
  "pipeline": "northstar.review.v1"
}
```
