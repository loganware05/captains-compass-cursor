# M3 validation evidence — m3-evaluator-experience-routing

Date: 2026-08-24  
Branch: `feature/45-m3-evaluator-experience-routing`  
Issue: #45

## Commands

| Command | Result |
|---|---|
| Orchestrator unittest | 84 passed |
| `./scripts/doctor.sh` | 0 errors |
| `./tests/evals/run.sh` | 38 passed |
| `./tests/run.sh` | 114 passed |

## Safety

- Routing proposals `auto_apply: false`; WEIGHTS unchanged
- Candidate ceiling `SANDBOX_TESTED`
- Proficiency requires Captain flag for authoritative use
