# Evidence — M35 / C2 Product-repo install (bitcoin-data-collector)

Date: 2026-09-16  
Plan: `c2-product-repo-install` (Captain approved)  
Release target: v1.38.0  
Rollback: `rollback/pre-c2-product-repo-install`  
Issue: [#164](https://github.com/loganware05/captains-compass-cursor/issues/164)

## Result

Local `install.sh` into `loganware05/bitcoin-data-collector` **succeeded** at
control `VERSION=1.38.0` (original product commit `0b7bb96`).

**Product PR opened** (APPLY Option A via Cloud Agent with write access):

| Item | Value |
|---|---|
| Product PR | https://github.com/loganware05/bitcoin-data-collector/pull/7 |
| Branch | `cursor/m35-c2-northstar-install-5182` |
| Base | `cursor/kalshi-live-decision-system` |
| Applied commit | `468c948` (`git am` of evidence patch; content-aligned with `0b7bb96`) |

| Artifact | Purpose |
|---|---|
| `install.log.txt` | scrubbed install.sh stdout (v1.38.0) |
| `INVENTORY.md` | Locks + SHA alignment with patch |
| `bitcoin-data-collector-install.patch` | `git format-patch` of product commit `0b7bb96` |
| `APPLY.md` | Captain / agent steps to push product PR |
| `SECRETS_SCAN.md` | high-signal secret pattern scan (clean) |
| `doctor.txt` | control doctor after C2 changes |

## Locks verified (local product tree + product PR branch)

- No `scripts/` directory / no `scripts/northstar`
- Install rewrites bare `./scripts/` → `$CONTROL/scripts/` in Skills/agents/commands/integrations
- `.cursor/install.sh` + `.cursor/environment.json` (Cloud Agent) preserved
- Product-scoped `docs/INDEX.md` relative links resolve; learn uses `$(pwd)`
- Memory templates added (repo had none prior)
- `.agent/COMPASS_VERSION` = `1.38.0` (matches control VERSION + install log)

## Status

**READY FOR MERGE** — control evidence + installer fix + **product PR #7** open.
Full C2 exit = merge product PR #7 + merge control PR #166 + tag **v1.38.0**.

## Residual Captain action

Review/merge:

1. Product [PR #7](https://github.com/loganware05/bitcoin-data-collector/pull/7)
2. Control [PR #166](https://github.com/loganware05/captains-compass-cursor/pull/166)
3. Tag `v1.38.0` on control after #166 merges
