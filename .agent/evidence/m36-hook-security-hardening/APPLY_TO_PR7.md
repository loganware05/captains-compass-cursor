# Refresh bitcoin-data-collector PR #7 with M36 hooks

From a checkout of PR #7 branch:

```bash
CONTROL=/path/to/captains-compass-cursor   # this branch / v1.38.1
PRODUCT=/path/to/bitcoin-data-collector    # PR #7 branch
cp "$CONTROL/.cursor/hooks/plan-approval-check.sh" "$PRODUCT/.cursor/hooks/"
cp "$CONTROL/.cursor/hooks/protected-branch.sh" "$PRODUCT/.cursor/hooks/"
cp "$CONTROL/.cursor/hooks/README.md" "$PRODUCT/.cursor/hooks/"
# optional: bump recorded version if you track it
echo 1.38.1 > "$PRODUCT/.agent/COMPASS_VERSION"
cd "$PRODUCT"
git add .cursor/hooks .agent/COMPASS_VERSION
git commit -m "fix(hooks): M36 fail-closed plan-approval + protected-branch hardening"
git push
```

Or copy the files from `.agent/evidence/m36-hook-security-hardening/` in this evidence folder.
