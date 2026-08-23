# M2 validation evidence — m2-execution-telemetry-ti

Date: 2026-08-23  
Branch: `feature/41-m2-execution-telemetry-ti`  
Issue: #41

## Commands

| Command | Result |
|---|---|
| `PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_*.py'` | 75 passed |
| `./scripts/doctor.sh` | 0 errors |
| `./tests/evals/run.sh` | 31 passed |
| `./tests/run.sh` | 111 passed |

## Sensors covered

- Experience + ExecutionRun schemas
- Telemetry store path-safety
- File TI redacted Stars fixtures + NOT APPROVED banner
- Stub TI default isolation
- Candidate promotion DISCOVERED → ANALYZED staging
- experience-skill-training draft from fixture
- Registry skill count 27
- record-execution-run smoke

## Safety notes

- Candidates always `approved_for_execution: false`
- Drafts land under `.agent/capabilities/candidates/` only
- No live network TI in CI
