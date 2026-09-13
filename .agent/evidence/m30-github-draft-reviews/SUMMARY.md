# Evidence — M30 Opt-in GitHub draft reviews

Date: 2026-09-13  
Plan: `m30-github-draft-reviews` (Captain approved)  
Release target: v1.33.0  
Rollback: `rollback/pre-m30-github-draft-reviews`

## Artifacts

| File | What it proves |
|---|---|
| `doctor.txt` | Doctor green including github draft module/schema/template |
| `unittest.txt` | `tests/orchestrator/test_m30_github_draft.py` green |
| `refuse.json` | Non-allowlisted repo refused (`github_review_posted` stays false) |
| `posted-mock.json` | Mock PENDING draft post for sandbox allowlist; token redacted |

## Locks verified

- Default path does not post
- Allowlist refuse-closed
- PENDING draft only (no `event` / no APPROVE / REQUEST_CHANGES)
- Tokens absent from evidence payloads
