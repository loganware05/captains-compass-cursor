# Evidence — M29 Intent packs + installer templates

Date: 2026-09-13  
Plan: `m29-intent-packs` (Captain approved)  
Release target: v1.32.0  
Rollback: `rollback/pre-m29-intent-packs`

## Artifacts

| File | What it proves |
|---|---|
| `doctor.txt` | Doctor green including intent module/schema/template/export |
| `unittest.txt` | `tests/orchestrator/test_m29_intent_packs.py` green |
| `export-log.txt` + `exported-intent.json` | Linear fixture export; `captain_approval=false` |
| `install-log.txt` | Installer adds `INTENT_PACK.md` + `.agent/intent/` without clobbering existing plans |
| `review-intent-json.json` | Review via `--intent-json` only (no temp plan) |
| `review-autodiscover.json` | Review via installed intent artifact auto-discover |
| `m29-evidence-intent-json/` | Full evidence report tree for intent-json run |

## Locks verified

- Hermetic / no model on default path
- `captain_approval` forced false on export + load
- No GitHub review posting
- Installer skip-if-exists for existing `IMPLEMENTATION_PLAN.md`
