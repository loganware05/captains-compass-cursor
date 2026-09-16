# Apply — bitcoin-data-collector NorthStar install

Control bot lacks push permission to `loganware05/bitcoin-data-collector` (403).
Local install succeeded at control v1.38.0; this patch is the product PR payload
(commit `0b7bb96`).

## Option A — apply patch (Captain machine)

```bash
git clone https://github.com/loganware05/bitcoin-data-collector.git
cd bitcoin-data-collector
git checkout cursor/kalshi-live-decision-system
git checkout -b cursor/m35-c2-northstar-install-3b10
git am /path/to/captains-compass-cursor/.agent/evidence/c2-product-repo-install/bitcoin-data-collector-install.patch
git push -u origin cursor/m35-c2-northstar-install-3b10
# Open PR → base: cursor/kalshi-live-decision-system
```

## Option B — re-run install from control

```bash
CONTROL=/path/to/captains-compass-cursor   # at v1.38.0 / this PR
PRODUCT=/path/to/bitcoin-data-collector
cd "$PRODUCT"
git checkout cursor/kalshi-live-decision-system
git checkout -b cursor/m35-c2-northstar-install-3b10
"$CONTROL/scripts/install.sh" "$(pwd)"
# Confirm: no scripts/; no bare ./scripts/ in Skills/docs; .cursor/install.sh preserved
git add -A && git commit -m "chore(workflow): install NorthStar without control scripts"
git push -u origin HEAD
```

## Locks verified locally

- No `scripts/` directory in product after install
- Bare `./scripts/` rewritten to `$CONTROL/scripts/` in Skills/agents/commands/integrations
- Cloud Agent `.cursor/install.sh` + `environment.json` preserved
- Product `docs/INDEX.md` is product-scoped (relative links resolve; `--repo "$(pwd)"`)
- Memory templates added (new repo had none)
- `.agent/COMPASS_VERSION` = `1.38.0`
