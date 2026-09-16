# Apply — bitcoin-data-collector NorthStar install

**Status: APPLIED** — product PR open:

https://github.com/loganware05/bitcoin-data-collector/pull/7  
Branch: `cursor/m35-c2-northstar-install-5182` → base `cursor/kalshi-live-decision-system`  
Commit: `468c948` (`git am` of this patch; aligned with original `0b7bb96`)

Control bot initially lacked push permission (403). A later Cloud Agent with write
access applied Option A successfully (2026-09-16).

## Option A — apply patch (done)

```bash
git clone https://github.com/loganware05/bitcoin-data-collector.git
cd bitcoin-data-collector
git checkout cursor/kalshi-live-decision-system
git checkout -b cursor/m35-c2-northstar-install-5182
git am /path/to/captains-compass-cursor/.agent/evidence/c2-product-repo-install/bitcoin-data-collector-install.patch
git push -u origin cursor/m35-c2-northstar-install-5182
# PR → base: cursor/kalshi-live-decision-system
```

## Option B — re-run install from control (alternate)

```bash
CONTROL=/path/to/captains-compass-cursor   # at v1.38.0 / this PR
PRODUCT=/path/to/bitcoin-data-collector
cd "$PRODUCT"
git checkout cursor/kalshi-live-decision-system
git checkout -b cursor/m35-c2-northstar-install-5182
"$CONTROL/scripts/install.sh" "$(pwd)"
# Confirm: no scripts/; no bare ./scripts/ in Skills/docs; .cursor/install.sh preserved
git add -A && git commit -m "chore(workflow): install NorthStar without control scripts"
git push -u origin HEAD
```

## Locks verified on product PR branch

- No `scripts/` directory in product after install
- Bare `./scripts/` rewritten to `$CONTROL/scripts/` in Skills/agents/commands/integrations
- Cloud Agent `.cursor/install.sh` + `environment.json` preserved
- Product `docs/INDEX.md` is product-scoped (relative links resolve; `--repo "$(pwd)"`)
- Memory templates added (new repo had none)
- `.agent/COMPASS_VERSION` = `1.38.0`
