# NorthStar live ops (M22 / v1.27.0)

Unattended GitHub webhook ingress and injectable-transport live adapters for the
NorthStar connected routine. **Fixture mode remains the CI default.**

## Fail-closed rules

1. Canonical approval is **GitHub + matching `plan_digest` only**.
2. Slack and Linear never approve or dispatch (`authoritative: false`).
3. Product dispatch allowlist is sandbox-only:
   `loganware05/captain-compass-sandbox`.
4. Live mode requires explicit `--mode live` and secrets from the environment
   (never committed).
5. Webhooks require `X-Hub-Signature-256` HMAC-SHA256; unsigned → 401.
6. Wrong Cursor agent → `BLOCKED_AGENT_IDENTITY` (M21 pin preserved).
7. No auto-merge, auto-release, live Skill install, or weight auto-apply.

## Modes

| Mode | Behavior |
|---|---|
| `fixtures` (default) | In-memory / store_dir adapters; CI-safe; `--approve` may fabricate GitHub approval for demos |
| `live` | Outbound via `HttpTransport`; `--approve` **refused**; approval only from GitHub `NORTHSTAR_APPROVE plan_digest=<64-hex>` |

## Environment (never commit)

| Variable | Purpose |
|---|---|
| `NORTHSTAR_MODE` | Optional default mode hint |
| `NORTHSTAR_PRODUCT_REPO` | Must be sandbox allowlist |
| `NORTHSTAR_GITHUB_WEBHOOK_SECRET` | Ingress HMAC secret |
| `NORTHSTAR_GITHUB_TOKEN` | Live GitHub REST |
| `NORTHSTAR_LINEAR_API_KEY` | Live Linear GraphQL |
| `NORTHSTAR_SLACK_BOT_TOKEN` | Live Slack notify |
| `NORTHSTAR_CAPTAIN_GITHUB_IDS` | Comma-separated Captain GitHub logins |

## Ingress

```bash
./scripts/serve-northstar-ingress.sh --mode fixtures   # healthz only; webhooks 503
./scripts/serve-northstar-ingress.sh --mode live --bind 127.0.0.1 --port 8787
```

Endpoints:

- `GET /healthz`
- `POST /webhooks/github` (live only; signature + allowlist + idempotent `X-GitHub-Delivery`)

## Routine CLI

```bash
./scripts/run-northstar-routine.sh --demo
./scripts/run-northstar-routine.sh --mode live --product-repo loganware05/captain-compass-sandbox \
  --provider github --event path/to/normalized.json
```

## Tests

CI uses `RecordingTransport` doubles — no live credentials:

```bash
python3 -m unittest tests.orchestrator.test_m22_northstar_live -v
```

## Related

- Skill: `.cursor/skills/northstar-connected-routine/SKILL.md`
- ADR-039 in `DECISIONS.md`
- Provider notes: `github.md`, `linear.md`, `slack.md`
