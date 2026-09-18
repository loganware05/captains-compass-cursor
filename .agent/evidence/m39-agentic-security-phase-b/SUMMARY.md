# Evidence — M39 agentic security Phase B ingest

Opt-in Cursor Security Reviewer / `/review-security` artifact ingest.

- Module: `orchestrator/review/agentic_security_ingest.py`
- CLI: `scripts/ingest-agentic-security.sh`
- Launcher: `northstar review ingest-agentic-security`
- Allowlist template: `templates/agent/review/agentic-security-allowlist.yml`
- Fixture: `tests/fixtures/code-review/agentic-security-sample.json`

Validation: `python3 -m unittest tests.orchestrator.test_m39_agentic_security_ingest`

Locks: hermetic `northstar review` default unchanged; refuse-closed without
`enabled: true` + allowlisted `owner/repo`.

## Landing note (2026-09-18)

Feature landed on `main` via **#175** (`cursor/m39-agentic-security-phase-b-5182`).
Parallel track **#176** (`…-3b10`) was rebased as a docs/conflict closeout after
#173/#175 — no second implementation.
