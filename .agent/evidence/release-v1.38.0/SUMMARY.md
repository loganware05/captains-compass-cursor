# Release v1.38.0

| Field | Value |
|---|---|
| Tag | `v1.38.0` @ `c8c1345` |
| Milestone | M35 / C2 product-repo install |
| Control PR | https://github.com/loganware05/captains-compass-cursor/pull/166 |
| Product PR | https://github.com/loganware05/bitcoin-data-collector/pull/7 |
| Tagged | 2026-09-17 |

## Notes

NorthStar install into `bitcoin-data-collector` without copying control `scripts/`.
Installer rewrites bare `./scripts/` → `$CONTROL/scripts/`. Follow-on: M36 hook
hardening (PR #167) → v1.38.1.
