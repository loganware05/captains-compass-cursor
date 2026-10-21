# Optional post-merge oversight hook (docs-only)

NorthStar does **not** install git hooks by default. Operators who want
post-merge oversight can add a local hook that invokes the CLI.

Example `.git/hooks/post-merge` (executable):

```bash
#!/usr/bin/env bash
set -euo pipefail
# Run from a control-repo checkout that has scripts/northstar, or set CONTROL.
CONTROL="${NORTHSTAR_CONTROL_ROOT:-$(git rev-parse --show-toplevel)}"
if [[ -x "$CONTROL/scripts/run-oversight.sh" ]]; then
  COMPASS_STATUS_ENABLED=1 COMPASS_BRAIN_ENABLED=1 \
    "$CONTROL/scripts/run-oversight.sh" --repo-root "$(git rev-parse --show-toplevel)" \
    --since "ORIG_HEAD" || true
fi
```

Notes:

- Proposal-only — never auto-applies memory edits.
- Prefer explicit `northstar oversight run` / `status post-merge` in CI or
  closeout checklists over silent hooks.
