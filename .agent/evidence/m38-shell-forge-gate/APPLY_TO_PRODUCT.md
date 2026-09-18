# Refresh product hooks after M38 (shell forge gate)

After control M38 merges (v1.39.1):

```bash
CONTROL=/path/to/captains-compass-cursor
PRODUCT=/path/to/bitcoin-data-collector
cp "$CONTROL/.cursor/hooks/plan-approval-check.sh" "$PRODUCT/.cursor/hooks/"
cp "$CONTROL/.cursor/hooks.json" "$PRODUCT/.cursor/hooks.json"
# or merge beforeShellExecution entry for plan-approval-check.sh
echo 1.39.1 > "$PRODUCT/.agent/COMPASS_VERSION"
```
