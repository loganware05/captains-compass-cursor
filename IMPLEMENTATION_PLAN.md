# Implementation Plan — Parked: post-M20 path options

- Status: **PARKED** — Captain is drafting a separate **M21** plan; disregard options A–E here.
- Plan ID: `m21-roadmap-options` (superseded by Captain’s forthcoming M21 draft)
- Baseline: v1.24.0

## Active work: sandbox refresh (not a product change)

| Item | Status |
|---|---|
| Sandbox clone | Pass — https://github.com/loganware05/captain-compass-sandbox.git |
| Update 1.22.0 → 1.24.0 | Pass — doctor green; 21/21 tests |
| Local branch / commit | `chore/refresh-compass-1.24.0` @ `a9a7f0c` |
| Patch | `.agent/evidence/sandbox-refresh-1.24.0/` |
| Push / open sandbox PR | **Blocked** — `cursor[bot]` 403 (App installation lacks sandbox write) |

### Unblock (required)

1. GitHub → Settings → Applications → **Cursor** → Configure → add
   `loganware05/captain-compass-sandbox` under repository access (write).
2. Add `github.com/loganware05/captain-compass-sandbox` to this Cloud Agent
   environment repos list.
3. Reply so the agent can push and open the sandbox PR.

**Or** apply the patch with your credentials:

```bash
cd /path/to/captain-compass-sandbox
git checkout main && git pull
git checkout -b chore/refresh-compass-1.24.0
git am /path/to/captains-compass-cursor/.agent/evidence/sandbox-refresh-1.24.0/0001-chore-refresh-compass-1.24.0.patch
git push -u origin HEAD
gh pr create --title "chore: refresh Captain's Compass to v1.24.0" \
  --body "Refresh sandbox 1.22.0 → 1.24.0 (M19/M20). Doctor green; 21/21 tests."
```

## Parked roadmap options (do not use)

Captain will supply M21. Former options A–E (live learning / Pinecone / hygiene /
First Mate / custom) are **out of scope** until that plan lands.
