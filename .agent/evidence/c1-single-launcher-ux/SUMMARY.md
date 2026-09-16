# Evidence — M34 / C1 Single launcher UX

Date: 2026-09-16  
Plan: `c1-single-launcher-ux` (Captain approved)  
Release target: v1.37.0  
Rollback: `rollback/pre-c1-single-launcher-ux`  
Issue: [#161](https://github.com/loganware05/captains-compass-cursor/issues/161)

## Artifacts

| File | What it proves |
|---|---|
| `doctor.txt` | Doctor green including help surfaces + INDEX/onboarding |
| `unittest.txt` | `tests/orchestrator/test_m34_c1_single_launcher_ux.py` green |
| `northstar-help.txt` | Unified surface map + docs/INDEX.md pointer |

## Locks verified

- Control `scripts/` not copied on install (help + onboarding state boundary)
- Skill slug `code-reviewer` unchanged
- No C2 product-repo install in this release
- Hermetic path — no model / no network
