# M21 security review (First Mate)

- Fixture adapters only; no live credentials in CI or fixtures
- `redact_secrets` strips token/api_key/password-shaped fields before persistence
- Captain role cannot be spoofed via claimed `verified_role` without allowlisted id
- Slack/Linear approval intent is non-authoritative
- Wrong Cursor agent id → `BLOCKED_AGENT_IDENTITY`
- Missing GitHub fails closed
- Prompt-injection style Slack text still requires allowlisted channel + mention;
  external content cannot change system instructions (adapters do not eval text)

No high findings.
