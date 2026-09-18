# Refresh bitcoin-data-collector with M36 hooks (post-#7)

**Done:** Product PR [#8](https://github.com/loganware05/bitcoin-data-collector/pull/8)
(`cursor/m36-hooks-refresh-5182` → `cursor/kalshi-live-decision-system`) after C2 #7 merged.

Replay (if needed):

```bash
CONTROL=/path/to/captains-compass-cursor   # M36 / v1.38.1
PRODUCT=/path/to/bitcoin-data-collector    # from cursor/kalshi-live-decision-system
cp "$CONTROL/.cursor/hooks/plan-approval-check.sh" "$PRODUCT/.cursor/hooks/"
cp "$CONTROL/.cursor/hooks/protected-branch.sh" "$PRODUCT/.cursor/hooks/"
cp "$CONTROL/.cursor/hooks/README.md" "$PRODUCT/.cursor/hooks/"
echo 1.38.1 > "$PRODUCT/.agent/COMPASS_VERSION"
cd "$PRODUCT"
git add .cursor/hooks .agent/COMPASS_VERSION
git commit -m "fix(hooks): M36 fail-closed plan-approval + protected-branch hardening"
git push
```

Or copy from `.agent/evidence/m36-hook-security-hardening/` in this folder.
