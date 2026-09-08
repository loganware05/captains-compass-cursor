# Handoff: multi-repo Cloud Agent — sandbox 1.24.0 refresh

Use this when launching a **new** Cloud Agent whose environment includes:

- `https://github.com/loganware05/captains-compass-cursor`
- `https://github.com/loganware05/captain-compass-sandbox`

Prior agent (`bc-34aed931-3660-4895-a57d-87e062259568`) could not push to the
sandbox: GitHub App installation token for that run only saw
`captains-compass-cursor`. M21 path A–E is **parked** — Captain drafts M21 separately.

## Paste prompt (new Cloud Agent)

```
Continue Captain's Compass sandbox refresh to v1.24.0.

Context:
- Control repo: loganware05/captains-compass-cursor (main has v1.24.0 tagged/released)
- Sandbox repo: loganware05/captain-compass-sandbox (currently on Compass 1.22.0)
- Prior agent prepared the refresh but could not push (cursor[bot] 403). M21 A–E options are parked; ignore them. Captain will supply a separate M21 plan later.

Tasks (do these in order):
1. Verify write access: `gh api /installation/repositories` should list BOTH repos; `git push` to sandbox must work.
2. In captain-compass-sandbox: checkout main, create branch `chore/refresh-compass-1.24.0`.
3. From captains-compass-cursor (main / v1.24.0): run `./scripts/update.sh <sandbox-path>` then `./scripts/doctor.sh <sandbox-path>`.
4. In sandbox: `npm ci && npm test` (expect 21/21). Commit: `chore: refresh Captain's Compass to v1.24.0`.
5. Push branch and open a PR into sandbox `main` with body noting M19/M20 / doctor green / 21/21 tests.
6. In control repo, on a docs/chore branch: update `docs/SANDBOX_VALIDATION.md`, `PROGRESS.md`, and `.agent/evidence/release-v1.24.0/post-tag-validation.md` with the sandbox PR URL; open/update control PR (see #119).

Evidence already in control repo (optional apply instead of re-update):
`.agent/evidence/sandbox-refresh-1.24.0/0001-chore-refresh-compass-1.24.0.patch` (commit tip may be a9a7f0c from prior prep).

Do not start M21 product work. Stop after sandbox PR + control-doc update.
```

## API alternative (if you have a Cursor API key)

```bash
curl --request POST \
  --url https://api.cursor.com/v1/agents \
  -u "$CURSOR_API_KEY:" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "sandbox-1.24.0-refresh",
    "prompt": { "text": "SEE HANDOFF PROMPT ABOVE" },
    "repos": [
      { "url": "https://github.com/loganware05/captains-compass-cursor", "startingRef": "main" },
      { "url": "https://github.com/loganware05/captain-compass-sandbox", "startingRef": "main" }
    ],
    "autoCreatePR": true
  }'
```

## Control-repo references

- Plan/evidence PR: https://github.com/loganware05/captains-compass-cursor/pull/119
- Release: https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.24.0
- Sandbox: https://github.com/loganware05/captain-compass-sandbox
