# Sandbox refresh — Compass v1.24.0

Prepared by cloud agent. Push blocked for `cursor[bot]` until Cursor GitHub App
has write on `loganware05/captain-compass-sandbox`.

| Item | Value |
|---|---|
| From | 1.22.0 |
| To | 1.24.0 |
| Branch | `chore/refresh-compass-1.24.0` |
| Commit | `a9a7f0c571501bb188a57f19e245ac154bddae73` |
| Doctor | Pass (see `doctor.txt`) |
| Tests | 21/21 (see `npm-test.txt`) |
| Push | **Blocked** — Permission denied to cursor[bot] |

## Apply (Captain)

```bash
cd /path/to/captain-compass-sandbox
git checkout main && git pull
git checkout -b chore/refresh-compass-1.24.0
git am /path/to/captains-compass-cursor/.agent/evidence/sandbox-refresh-1.24.0/0001-chore-refresh-compass-1.24.0.patch
git push -u origin HEAD
gh pr create --title "chore: refresh Captain's Compass to v1.24.0" \
  --body "Refresh sandbox 1.22.0 → 1.24.0 (M19/M20). Doctor green; 21/21 tests."
```

Or grant Cursor GitHub App **write** on the sandbox + add it to the Cloud Agent
environment repos, then ask the agent to push.
