# M21 security review (First Mate)

- Fixture adapters only; no live credentials in CI or fixtures
- `redact_secrets` strips token/api_key/password-shaped fields before persistence
- Captain role cannot be spoofed via claimed `verified_role` without allowlisted id
- Slack/Linear approval intent is non-authoritative
- Wrong Cursor agent id → `BLOCKED_AGENT_IDENTITY` (legal from IN_PROGRESS/VALIDATING/DISPATCHED)
- `DISPATCHED` / `dispatch()` require `plan_approved` + `github:` approval ref + plan digest
- Checkpoints bind to `run_id` + `packet_digest` when a run is supplied
- Repo-global idempotency store prevents duplicate side effects across run_ids
- Missing GitHub fails closed
- Prompt-injection style Slack text still requires allowlisted channel + mention;
  external content cannot change system instructions (adapters do not eval text)

Adversarial review findings (CRITICAL/HIGH) addressed in follow-up commit on this branch.

No remaining high findings for the fixture path.
