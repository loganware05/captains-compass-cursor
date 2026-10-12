# M52 Overseer Skill + Live StatusProvider — Validation Evidence

- Plan: `m52-overseer-skill-live-provider` (OVA-68)
- Branch: `feature/OVA-68-m52-overseer-skill-live-provider`
- Rollback: `rollback/pre-m52-overseer-skill-live-provider` @ `bf5ee25`
- VERSION: **1.57.0**
- Date: 2026-10-11

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_m52_overseer_skill_live_provider.py' -v
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_m51_project_overseer.py' -q
./scripts/doctor.sh
COMPASS_STATUS_ENABLED=1 COMPASS_STATUS_PROVIDER=stub \
  ./scripts/northstar status explain --repo .
```

## Results

| Check | Result |
|---|---|
| M52 unittest (12) | PASS |
| M51 regression (15) | PASS |
| Doctor | PASS (0 errors) — Skill/agent/schema + status fail-closed; skill inodes rebuilt (44) |
| Stub explain | Writes system-map + scope-ledger under `.agent/status/` |
| HTTP without keys | Fail closed (`StatusServiceError`) |

## Invariants

- CI does not require live HTTP/Kimi
- Canonical memory docs not auto-rewritten
- `approved_for_execution: false` / `authority_mutation: false`
