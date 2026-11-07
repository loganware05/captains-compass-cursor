# Security — i1-sentry-incident-intelligence (#249)

- Fail-closed ingest + live dual gates
- https-only live API base
- Read-only token expected; `write_to_sentry` const false
- Stack excerpts redacted via `redact_secrets`
- Packets claim_kind external; Overseer refs non-authoritative
