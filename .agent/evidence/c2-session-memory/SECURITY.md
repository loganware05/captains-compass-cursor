# Security notes — C2 session memory

- Dual fail-closed gates: `COMPASS_BRAIN_ENABLED` + `COMPASS_SESSION_MEMORY_ENABLED`.
- Runtime store `.agent/session-memory/**` gitignored; fixtures only in tests/.
- Secret-pattern reject on ingest (api_key / password / token / cookie).
- Authority consts `approved_for_execution` / `authority_mutation` always false.
- No hosted observer, no default telemetry, no auto capture hooks in v1.86.0.
- Never rewrites PROJECT_CONTEXT / DECISIONS / AGENTS.
