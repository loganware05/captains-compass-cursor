# Evidence — M35 / C2 Product-repo install (bitcoin-data-collector)

Date: 2026-09-16  
Plan: `c2-product-repo-install` (Captain approved)  
Release target: v1.38.0  
Rollback: `rollback/pre-c2-product-repo-install`  
Issue: [#164](https://github.com/loganware05/captains-compass-cursor/issues/164)

## Result

Local `install.sh` into `loganware05/bitcoin-data-collector` **succeeded**.
Push of product branch `cursor/m35-c2-northstar-install-3b10` **failed** (GitHub 403 —
`cursor[bot]` lacks write access to that repo).

| Artifact | Purpose |
|---|---|
| `install.log` | install.sh stdout |
| `INVENTORY.md` | Locks: no `scripts/`; cloud venv install preserved; COMPASS_VERSION |
| `bitcoin-data-collector-install.patch` | `git format-patch` of the product install commit |
| `APPLY.md` | Captain steps to push product PR |

## Locks verified (local product tree)

- No `scripts/` directory / no `scripts/northstar`
- `.cursor/install.sh` + `.cursor/environment.json` (Cloud Agent) preserved
- Product-scoped `docs/INDEX.md` relative links resolve
- Memory templates added (repo had none prior)
- `.agent/COMPASS_VERSION` = `1.38.0`

## Captain follow-up (required for full C2 exit)

Apply `APPLY.md` (patch or re-install) and open the product PR against
`cursor/kalshi-live-decision-system`, **or** grant the Cloud Agent write access
to `bitcoin-data-collector` and ask First Mate to push.
