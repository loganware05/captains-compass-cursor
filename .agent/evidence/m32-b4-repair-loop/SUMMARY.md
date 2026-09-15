# Evidence — M32 / B4 Repair loop

Date: 2026-09-15  
Plan: `b4-repair-loop` (Captain approved)  
Release target: v1.35.0  
Rollback: `rollback/pre-b4-repair-loop`  
Issue: [#154](https://github.com/loganware05/captains-compass-cursor/issues/154)

## Artifacts

| File | What it proves |
|---|---|
| `doctor.txt` | Doctor green including repair module + `run-repair.sh` |
| `unittest.txt` | `tests/orchestrator/test_m32_repair_loop.py` green |
| `record-result.json` | CLI dry-run summary (`merged=false`, `auto_merge=false`) |
| `sample-run/` | Full evidence packet for `sec-secret-in-diff` |

## Locks verified

- Unverified / below-floor findings refused (unit tests)
- Non-allowlisted `--prepare-pr` refused
- Draft PR metadata only; never merged
- Live Cursor dispatch never invoked
- Hermetic path — no model / no network required
